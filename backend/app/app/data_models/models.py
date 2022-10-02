from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


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


class JobBase(BaseModel):
    repository: str
    status_id: str
    job_type_id: str
    user: Optional[str] = None
    version: Optional[str] = None  # Git: ref
    artifact_urls: List[str] = []
    worker_version: Optional[str] = None
    error_message: Optional[str] = None
    style: Optional[str] = None


class JobCreate(JobBase):
    pass


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
    # content_server: Optional[ContentServer]
    job_type: JobType

    class Config:
        orm_mode = True


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
