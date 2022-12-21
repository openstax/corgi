
from asyncio import AbstractEventLoop
from asyncio.locks import Lock
from datetime import datetime
from typing import Dict, Generator, List, Optional, Union, cast

from app.core.errors import CustomBaseError
from app.data_models.models import Job as JobModel
from app.data_models.models import JobCreate, JobUpdate, UserSession
from app.db.base_class import Base as BaseSchema
from app.db.schema import Book, BookJob, Commit, Repository
from app.db.schema import Jobs as JobSchema
from app.github import (AuthenticatedClient, GitHubRepo, get_book_repository,
                        get_collections)
from app.service.base import ServiceBase
from app.service.repository import repository_service
from app.service.user import user_service
from app.xml_utils import xpath1

from lxml import etree
from pydantic import BaseModel
from sqlalchemy.orm import Session


class CountedLock(Lock):
    def __init__(self, *, loop: Union[AbstractEventLoop, None] = None) -> None:
        super().__init__(loop=loop)
        self._counter = 0

    async def acquire(self):
        self._counter += 1
        return await super().acquire()

    def release(self):
        self._counter -= 1
        return super().release()

    @property
    def count(self):
        return self._counter


def get_or_create_repository(
        db: Session,
        repo_name: str,
        repo_owner: str,
        github_repo: GitHubRepo,
        user: UserSession) -> Repository:
    # Check if the repository exists
    db_repo = cast(Optional[Repository], db.query(Repository).filter(
        Repository.name == repo_name,
        Repository.owner == repo_owner).first())
    # If not, record it and associate it with the user
    if db_repo is None:
        db_repo = Repository(
            id=github_repo.database_id,
            name=repo_name,
            owner=repo_owner)
        repository_service.upsert_repositories(db, [db_repo])
        user_service.upsert_user_repositories(
            db, user, [github_repo])
    return db_repo


def add_books_to_commit(
        db: Session,
        commit: Commit,
        repo_books: List[dict],
        collections_by_name: Dict[str, etree.ElementBase]):
    for repo_book in repo_books:
        slug = repo_book["slug"]
        style = repo_book["style"]
        collection = collections_by_name[f"{slug}.collection.xml"]
        uuid = xpath1(collection, "//*[local-name()='uuid']").text
        if not uuid:
            raise CustomBaseError("Could not get uuid from collection xml")
        # TODO: Edition should be either nullable or in a different table
        db_book = Book(uuid=uuid, slug=slug, edition=0, style=style)
        commit.books.append(db_book)
        db.add(db_book)


def add_books_to_job(
        db: Session,
        job: JobSchema,
        books: Union[List[Book], Generator[Book, None, None]]):
    for db_book in books:
        book_job = BookJob(book_id=db_book.id)
        job.books.append(book_job)
        db.add(book_job)


class JobsService(ServiceBase):
    """If specific methods need to be overridden they can be done here.
    """

    def __init__(self, schema_model: BaseSchema, data_model: BaseModel):
        super().__init__(schema_model, data_model)
        self._locks_by_name: Dict[str, CountedLock] = {}

    async def create(
            self,
            client: AuthenticatedClient,
            db: Session,
            job_in: JobCreate,
            user: UserSession) -> JobModel:

        repo_name = job_in.repository.name
        repo_owner = job_in.repository.owner
        version = job_in.version is not None and job_in.version or "main"
        repo_book_in = job_in.book

        github_repo, sha, timestamp, repo_books = await get_book_repository(
            client, repo_name, repo_owner, version)

        # If the user supplied an invalid argument for book
        if repo_book_in is not None:
            if not any(b["slug"] == repo_book_in for b in repo_books):
                raise CustomBaseError(f"Book not in repository '{repo_book_in}'")
        else:
            # Until we can build multiple books
            raise CustomBaseError("Book is required")
        repo_lock = self._locks_by_name.get(repo_name, None)
        if repo_lock is None:
            repo_lock = self._locks_by_name[repo_name] = CountedLock()
        async with repo_lock:
            commit = cast(Optional[Commit], db.query(Commit).filter(
                Commit.sha == sha).first())
            # If the commit has been record and has books, reuse the existing
            # data
            if (commit is not None and len(commit.books) != 0
                    and commit.repository.owner == repo_owner):
                db_repo = commit.repository
                # Check to see if the user has been associated with this repo
                if not any(ur.user.id == user.id for ur in db_repo.users):
                    # If not, get the information we need and add the association
                    # Use `get_repository` to get the viewer_permission
                    user_service.upsert_user_repositories(
                        db, user, [github_repo])
            else:
                db_repo = get_or_create_repository(db, repo_name, repo_owner,
                                                   github_repo, user)
                # Now we can record the commit
                commit = Commit(repository_id=db_repo.id, sha=sha,
                                timestamp=timestamp, books=[])
                db.add(commit)
                # And record all the book metadata
                collections_by_name = await get_collections(client, repo_name,
                                                            repo_owner, sha)
                add_books_to_commit(db, commit, repo_books, collections_by_name)

                # Flush the db to populate autogenerated book and commit ids
                db.flush()
            db_job = JobSchema(user_id=user.id,
                               status_id=job_in.status_id,
                               job_type_id=job_in.job_type_id,
                               worker_version=job_in.worker_version)
            db.add(db_job)

            # And, finally, associate each book with the job          
            books_for_job = commit.books
            if repo_book_in is not None:
                books_for_job = (
                    b for b in books_for_job if b.slug == repo_book_in)
            add_books_to_job(db, db_job, books_for_job)

            db.commit()
        # Last one out turns out the lights
        if repo_lock.count == 0:
            del self._locks_by_name[repo_name]
        return db_job

    def update(self, db_session: Session, job: JobSchema, job_in: JobUpdate):
        if isinstance(job_in.artifact_urls, list):
            book_job_by_book_slug = {b.book.slug: b for b in job.books}
            for artifact_url in job_in.artifact_urls:
                book_job_by_book_slug[artifact_url.slug].artifact_url = \
                    artifact_url.url
        elif job_in.artifact_urls is not None:
            job.books[0].artifact_url = job_in.artifact_urls
        return super().update(db_session, job, job_in, JobUpdate)

    def get_jobs_in_date_range(
            self,
            db: Session,
            start: datetime,
            end: datetime,
            order_by: Optional[List] = None) -> List[JobSchema]:
        query = db.query(JobSchema).filter(
            JobSchema.created_at >= start, JobSchema.created_at <= end
        )
        if order_by is not None:
            query = query.order_by(*order_by)
        return query.all()


jobs_service = JobsService(JobSchema, JobModel)
