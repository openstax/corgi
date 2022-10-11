from datetime import datetime
from app.db.schema import Repository

from pydantic import BaseModel
from pydantic.utils import GetterDict
from typing import List, Optional, Any


class StatusBase(BaseModel):
    name: str


class Status(StatusBase):
    id: str

    class Config:
        orm_mode = True


# class ContentServerBase(BaseModel):
#     hostname: str
#     host_url: str
#     name: str


# class ContentServer(ContentServerBase):
#     id: str

#     class Config:
#         orm_mode = True


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


class RepositoryBase(BaseModel):
    name: str
    owner: str


class JobGetter(GetterDict):
    def get(self, key: str, default: Any) -> Any:
        # How to get information from child tables
        if key == 'repository':
            return self._obj.books[0].book.commit.repository
        else:
            try:
                return getattr(self._obj, key)
            except (AttributeError, KeyError):
                return default


class Repository(RepositoryBase):
    id: str

    class Config:
        orm_mode = True


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
    error_message: Optional[str] = None
    style: Optional[str] = None


class JobCreate(JobBase):
    repository: RepositoryBase
    book: Optional[str] = None


class JobUpdate(BaseModel):
    status_id: str
    pdf_url: Optional[str] = None
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
    artifact_urls: List[str] = []


    class Config:
        orm_mode = True
        getter_dict = JobGetter


class GitHubRepo(BaseModel):
    name: str
    database_id: str
    viewer_permission: str

    @classmethod
    def from_node(cls, node: dict):
        def to_snake_case(s: str):
            ret = []
            for c in s:
                if c.isupper():
                    ret.append("_")
                    ret.append(c.lower())
                else:
                    ret.append(c)
            return ''.join(ret)
        return cls(**{to_snake_case(k): v for k, v in node.items()})
