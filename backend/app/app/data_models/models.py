from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventBase(BaseModel):
    collection_id: str = None
    status_id: int = None
    pdf_url: Optional[str] = ""


class EventCreate(EventBase):
    collection_id: str
    status_id: int


class EventUpdate(BaseModel):
    status_id: int
    pdf_url: Optional[str]


class Event(EventBase):
    id: int
    collection_id: str
    status_id: int
    pdf_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
