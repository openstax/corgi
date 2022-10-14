
from datetime import datetime
from typing import Optional, cast

from app.github.client import AuthenticatedClient
from app.data_models.models import Job as JobModel
from app.data_models.models import JobCreate, UserSession
from app.db.schema import Book, BookJob, Commit
from app.db.schema import Jobs as JobSchema
from app.db.schema import Repository
from app.service.base import ServiceBase
from lxml import etree
from sqlalchemy.orm import Session as BaseSession


async def github_graphql(client: AuthenticatedClient, query: str):
    response = await client.post(
        "https://api.github.com/graphql", json={"query": query})
    response.raise_for_status()
    return response.json()


async def get_book_commit_metadata(client: AuthenticatedClient, repo_name: str,
                                   repo_owner: str, version: str):
    query = f"""
        query {{
            repository(name: "{repo_name}", owner: "{repo_owner}") {{
                object(expression: "{version}") {{
                    oid
                    ... on Commit {{
                        committedDate
                        file (path: "META-INF/books.xml") {{
                            object {{
                                ... on Blob {{
                                    text
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    payload = await github_graphql(client, query)
    commit = payload["data"]["repository"]["object"]
    commit_sha = commit["oid"]
    commit_timestamp = commit["committedDate"]
    fixed_timestamp = f"{commit_timestamp[:-1]}+00:00"
    books_xml = commit["file"]["object"]["text"]
    meta = etree.fromstring(books_xml, parser=None)

    books = [{ k: el.attrib[k] for k in ("slug", "style") } 
             for el in meta.xpath("//*[local-name()='book']")]
    return (commit_sha, datetime.fromisoformat(fixed_timestamp), books)


async def get_collections(client: AuthenticatedClient, repo_name: str,
                          repo_owner: str, commit_sha: str):
    query = f"""
        query {{
            repository(name: "{repo_name}", owner: "{repo_owner}") {{
                object(expression: "{commit_sha}") {{
                    ... on Commit {{
                        file (path: "collections") {{
                            object {{
                                ... on Tree {{
                                    entries {{
                                        name
                                        object {{
                                            ... on Blob {{
                                                text
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    payload = await github_graphql(client, query)
    files_entries = (payload["data"]["repository"]["object"]["file"]["object"]
                    ["entries"])
    return { entry["name"]: entry["object"]["text"]
            for entry in files_entries }


class JobsService(ServiceBase):
    """If specific methods need to be overridden they can be done here.
    """
    async def create(self, client: AuthenticatedClient, db_session: BaseSession,
                     job_in: JobCreate, user: UserSession) -> JobModel:
        repo_name =  job_in.repository.name
        repo_owner = job_in.repository.owner
        version = job_in.version is not None and job_in.version or "main"
        repo_book = job_in.book
        style = job_in.style is not None and job_in.style or "default"
        
        sha, timestamp, repo_books = await get_book_commit_metadata(
            client, repo_name, repo_owner, version)

        # If the user supplied an invalid argument for book
        if repo_book is not None:
            if not any(b["slug"] == repo_book for b in repo_books):
                raise Exception(f"Book not in repository {repo_book}")
        
        commit = cast(Optional[Commit], db_session.query(Commit).filter(
            Commit.sha == sha).first())
        if commit is not None and len(commit.books) != 0:
            repository = commit.repository
        else:
            repository = db_session.query(Repository).filter(
                Repository.name == repo_name, 
                Repository.owner == repo_owner).first()
            if repository is None:
                raise NotImplementedError("Should not happen atm")
            commit = Commit(repository_id=repository.id, sha=sha,
                            timestamp=timestamp, books=[])
            db_session.add(commit)
            collections_by_name = await get_collections(client, repo_name,
                                                        repo_owner, sha)
            for repo_book in repo_books:
                slug = repo_book["slug"]
                style = repo_book["style"]
                collection_xml = collections_by_name[f"{slug}.collection.xml"]
                collection = etree.fromstring(collection_xml, parser=None)
                uuid = collection.xpath("//*[local-name()='uuid']")[0].text
                # TODO: Edition should be either nullable or in a different 
                # table
                db_book = Book(uuid=uuid, slug=slug, edition=0, style=style)
                commit.books.append(db_book)
                db_session.add(db_book)
            db_session.flush()
            
        db_job = JobSchema(user_id=user.id,
                           status_id=job_in.status_id,
                           job_type_id=job_in.job_type_id,
                           style=style,
                           worker_version=job_in.worker_version)
        db_session.add(db_job)
        
        for db_book in commit.books:
            book_job = BookJob(book_id=db_book.id)
            db_job.books.append(book_job)
            db_session.add(book_job)
        
        db_session.commit()

        return db_job


jobs_service = JobsService(JobSchema, JobModel)
