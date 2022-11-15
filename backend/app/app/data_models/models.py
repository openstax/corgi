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
### Archive
# 1: pdf
# 2: distribution-preview
### Git
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


class Book(BookBase):
    uuid: str

    class Config:
        orm_mode = True


class JobGetter(GetterDict):
    def get(self, key: str, default: Any) -> Any:
        # How to get information from child tables
        if key == 'repository':
            return self._obj.books[0].book.commit.repository
        elif key == 'books':
            return [book_job.book for book_job in self._obj.books]
        elif key == 'artifact_urls':
            return [
                ArtifactBase(slug=book_job.book.slug,
                             url=book_job.artifact_url)
                for book_job in self._obj.books
            ]
        elif key == 'version':
            return self._obj.books[0].book.commit.sha
        else:
            try:
                return getattr(self._obj, key)
            except (AttributeError, KeyError):
                return default


class RepositoryGetter(GetterDict):
    def get(self, key: str, default: Any) -> Any:
        repository = self._obj
        if key == "books":
            books = set([])
            for commit in repository.commits:
                for book in commit.books:
                    books.add(book.slug)
            return list(books)
        else:
            try:
                return getattr(self._obj, key)
            except (AttributeError, KeyError):
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
    version: Optional[str] = None  # Git: ref
    worker_version: Optional[str] = None
    # error_message: Optional[str] = None


class JobCreate(JobBase):
    repository: RepositoryBase
    book: Optional[str] = None


class JobUpdate(BaseModel):
    status_id: str
    artifact_urls: Optional[Union[List[ArtifactBase], str]] = None
    worker_version: Optional[str] = None
    error_message: Optional[str] = None


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

