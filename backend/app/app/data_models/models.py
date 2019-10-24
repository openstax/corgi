from datetime import datetime

from pydantic import BaseModel


class StatusBase(BaseModel):
    name: str


class Status(StatusBase):
    id: str

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    collection_id: str
    status_id: str
    pdf_url: str = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    status_id: str
    pdf_url: str = None


class Event(EventBase):
    id: str
    created_at: datetime
    updated_at: datetime
    status: Status

    class Config:
        orm_mode = True
