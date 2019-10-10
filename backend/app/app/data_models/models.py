from datetime import datetime

from pydantic import BaseModel


class EventBase(BaseModel):
    book_id: str = None
    status_id: int = None


class EventCreate(EventBase):
    book_id: str
    status_id: int


class Event(EventBase):
    id: int
    book_id: str
    status_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
