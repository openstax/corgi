from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel
from pydantic.utils import GetterDict


class Role(int, Enum):
    USER = 1
    ADMIN = 9999
    DEFAULT = USER


class UserSession(BaseModel):
    id: int
    token: str
    role: Role
    avatar_url: str
    name: str

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN


class StatusBase(BaseModel):
    name: str


class Status(StatusBase):
    id: str

    class Config:
        orm_mode = True


class JobTypeBase(BaseModel):
    name: str
    display_name: str


# Types:
# Archive
# 1: pdf
# 2: distribution-preview
# Git
# 3: git-pdf
# 4: git-distribution-preview


class JobType(JobTypeBase):
    id: str

    class Config:
        orm_mode = True


class ArtifactBase(BaseModel):
    slug: str
    url: Optional[str] = None


class BookBase(BaseModel):
    slug: str
    commit_id: str
    edition: int
    style: str


class BaseApprovedBook(BaseModel):
    commit_sha: str
    uuid: str


class RequestApproveBook(BaseApprovedBook):
    code_version: str


class ApprovedBook(RequestApproveBook):
    created_at: datetime
    committed_at: datetime
    repository_name: str
    slug: str
    consumer: str
    style: str

    class Config:
        class Getter(GetterDict):
            getters = {
                "uuid": lambda self: self._obj.book.uuid,
                "commit_sha": lambda self: self._obj.book.commit.sha,
                "code_version": lambda self: self._obj.code_version.version,
                "consumer": lambda self: self._obj.consumer.name,
                "created_at": lambda self: self._obj.created_at,
                "committed_at": lambda self: self._obj.book.commit.timestamp,
                "repository_name": (
                    lambda self: self._obj.book.commit.repository.name
                ),
                "slug": lambda self: self._obj.book.slug,
                "style": lambda self: self._obj.book.style,
            }

            def get(self, key: str, default: Any = None) -> Any:
                return self.getters.get(key, lambda _: default)(self)

        orm_mode = True
        getter_dict = Getter


class Book(BookBase):
    uuid: str

    class Config:
        orm_mode = True


class JobGetter(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        # How to get information from child tables
        if key == "repository":
            return self._obj.books[0].book.commit.repository
        elif key == "books":
            return [book_job.book for book_job in self._obj.books]
        elif key == "artifact_urls":
            return [
                ArtifactBase(slug=book_job.book.slug, url=book_job.artifact_url)
                for book_job in self._obj.books
            ]
        elif key == "version":
            return self._obj.books[0].book.commit.sha
        # probably add information about approved versions
        else:
            try:
                return getattr(self._obj, key)
            except (AttributeError, KeyError):  # pragma: no cover
                return default


class RepositoryGetter(GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        repository = self._obj
        if key == "books":
            commits = (c for c in repository.commits if len(c.books) > 0)
            newest = max(commits, key=lambda c: c.timestamp, default=None)
            if newest is None:
                return []
            return [book.slug for book in newest.books]
        else:
            try:
                return getattr(self._obj, key)
            except (AttributeError, KeyError):  # pragma: no cover
                return default


class RepositoryBase(BaseModel):
    name: str
    owner: str


class Repository(RepositoryBase):
    class Config:
        orm_mode = True


class RepositorySummary(RepositoryBase):
    books: List[str]

    class Config:
        orm_mode = True
        getter_dict = RepositoryGetter


class UserBase(BaseModel):
    name: str
    avatar_url: str


class User(UserBase):
    id: str

    class Config:
        orm_mode = True


class JobBase(BaseModel):
    status_id: str
    job_type_id: str
    version: Optional[str] = None  # sha
    git_ref: Optional[str] = None  # branch, tag, or sha
    worker_version: Optional[str] = None


class JobCreate(JobBase):
    repository: RepositoryBase
    book: Optional[str] = None


class JobUpdate(BaseModel):
    status_id: str
    artifact_urls: Optional[Union[List[ArtifactBase], str]] = None
    worker_version: Optional[str] = None
    error_message: Optional[str] = None


class JobMin(BaseModel):
    id: str
    status_id: str
    job_type_id: str

    class Config:
        orm_mode = True
        getter_dict = JobGetter


class Job(JobBase):
    id: str
    created_at: datetime
    updated_at: datetime
    status: Status
    repository: Repository
    job_type: JobType
    user: User
    books: List[Book] = []
    artifact_urls: List[ArtifactBase] = []

    class Config:
        orm_mode = True
        getter_dict = JobGetter
