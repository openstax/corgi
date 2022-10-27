
from datetime import datetime
from typing import List, Optional, cast

from app.data_models.models import Job as JobModel
from app.data_models.models import JobCreate, JobUpdate, UserSession
from app.db.schema import Book, BookJob, Commit
from app.db.schema import Jobs as JobSchema
from app.db.schema import Repository
from app.github import (AuthenticatedClient, get_book_commit_metadata,
                        get_collections)
from app.service.base import ServiceBase
from lxml import etree
from sqlalchemy.orm import Session as BaseSession


class JobsService(ServiceBase):
    """If specific methods need to be overridden they can be done here.
    """
    async def create(self, client: AuthenticatedClient, db_session: BaseSession,
                     job_in: JobCreate, user: UserSession) -> JobModel:
        repo_name =  job_in.repository.name
        repo_owner = job_in.repository.owner
        version = job_in.version is not None and job_in.version or "main"
        repo_book_in = job_in.book
        style = job_in.style is not None and job_in.style or "default"
        
        sha, timestamp, repo_books = await get_book_commit_metadata(
            client, repo_name, repo_owner, version)

        # If the user supplied an invalid argument for book
        if repo_book_in is not None:
            if not any(b["slug"] == repo_book_in for b in repo_books):
                raise Exception(f"Book not in repository {repo_book_in}")
        
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
        
        books_for_job = commit.books
        if repo_book_in is not None:
            books_for_job = (b for b in books_for_job if b.slug == repo_book_in)
        for db_book in books_for_job:
            book_job = BookJob(book_id=db_book.id)
            db_job.books.append(book_job)
            db_session.add(book_job)
        
        db_session.commit()

        return db_job

    def update(self, db_session: BaseSession, job: JobSchema, job_in: JobUpdate):
        if isinstance(job_in.artifact_urls, list):
            book_job_by_book_slug = {b.book.slug: b for b in job.books}
            for artifact_url in job_in.artifact_urls:
                book_job_by_book_slug[artifact_url.slug].artifact_url = \
                    artifact_url.url
        elif job_in.artifact_urls is not None:
            job.books[0].artifact_url = job_in.artifact_urls
        return super().update(db_session, job, job_in, JobUpdate)

    def get_jobs_in_date_range(self, db_session: BaseSession, start: datetime,
                               end: datetime, order_by: Optional[List] = None):
        if order_by is None:
            order_by = [JobSchema.created_at.desc()]
        return db_session.query(JobSchema).filter(
            JobSchema.created_at >= start, JobSchema.created_at <= end
        ).order_by(*order_by).all()


jobs_service = JobsService(JobSchema, JobModel)
