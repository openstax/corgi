from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class Role(int, Enum):
    USER = 5000
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

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v)


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

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v)


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

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "book"):  # ORM object
            return {
                "uuid": data.book.uuid.lower(),
                "commit_sha": data.book.commit.sha.lower(),
                "code_version": data.code_version.version,
                "consumer": data.consumer.name,
                "created_at": data.created_at,
                "committed_at": data.book.commit.timestamp,
                "repository_name": data.book.commit.repository.name,
                "slug": data.book.slug,
            }
        return data


class Book(BookBase):
    uuid: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("commit_id", mode="before")
    @classmethod
    def coerce_commit_id(cls, v):
        return str(v)


class RepositoryBase(BaseModel):
    name: str
    owner: str


class Repository(RepositoryBase):
    model_config = ConfigDict(from_attributes=True)


class RepositorySummary(RepositoryBase):
    books: List[str]

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "commits"):  # ORM object
            commits = (c for c in data.commits if len(c.books) > 0)
            newest = max(commits, key=lambda c: c.timestamp, default=None)
            books = [book.slug for book in newest.books] if newest else []
            return {
                "name": data.name,
                "owner": data.owner,
                "books": books,
            }
        return data


class UserBase(BaseModel):
    name: str
    avatar_url: str


class User(UserBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v)


class PipelineVersionItem(BaseModel):
    position: int
    version: str

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "code_version"):  # ORM object
            return {
                "position": data.position,
                "version": data.code_version.version,
            }
        return data


class JobBase(BaseModel):
    status_id: str
    job_type_id: str
    version: Optional[str] = None  # sha
    git_ref: Optional[str] = None  # branch, tag, or sha
    worker_version: Optional[str] = None

    @field_validator("status_id", "job_type_id", mode="before")
    @classmethod
    def coerce_ids(cls, v):
        return str(v)


class JobCreate(JobBase):
    repository: RepositoryBase
    book: Optional[str] = None


class JobUpdate(BaseModel):
    status_id: Union[int, str]
    artifact_urls: Optional[Union[List[ArtifactBase], str]] = None
    worker_version: Optional[str] = None
    error_message: Optional[str] = None


class JobMin(BaseModel):
    id: str
    status_id: str
    job_type_id: str

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "books"):  # ORM object
            return {
                "id": str(data.id),
                "status_id": str(data.status_id),
                "job_type_id": str(data.job_type_id),
            }
        return data


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

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "books") and hasattr(
            data.books, "__iter__"
        ):  # ORM object
            return {
                "id": str(data.id),
                "created_at": data.created_at,
                "updated_at": data.updated_at,
                "status": data.status,
                "status_id": str(data.status_id),
                "job_type_id": str(data.job_type_id),
                "git_ref": data.git_ref,
                "worker_version": data.worker_version,
                "repository": data.books[0].book.commit.repository
                if data.books
                else None,
                "job_type": data.job_type,
                "user": data.user,
                "books": [book_job.book for book_job in data.books],
                "artifact_urls": [
                    ArtifactBase(slug=bj.book.slug, url=bj.artifact_url)
                    for bj in data.books
                ],
                "version": data.books[0].book.commit.sha
                if data.books
                else None,
            }
        return data
