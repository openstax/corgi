from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventBase(BaseModel):
    collection_id: str = None
    status_id: str = None
    pdf_url: str = None


class EventCreate(EventBase):
    collection_id: str
    status_id: str


class EventUpdate(BaseModel):
    status_id: str
    pdf_url: str = None


class Event(EventBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
