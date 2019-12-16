from datetime import datetime

from pydantic import BaseModel


class StatusBase(BaseModel):
    name: str


class Status(StatusBase):
    id: str

    class Config:
        orm_mode = True


class ContentServerBase(BaseModel):
    hostname: str
    host_url: str
    name: str


class ContentServer(ContentServerBase):
    id: str

    class Config:
        orm_mode = True


class JobBase(BaseModel):
    collection_id: str
    status_id: str
    pdf_url: str = None
    content_server_id: str
    version: str = None
    style: str = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    status_id: str
    pdf_url: str = None


class Job(JobBase):
    id: str
    created_at: datetime
    updated_at: datetime
    status: Status
    content_server: ContentServer

    class Config:
        orm_mode = True
