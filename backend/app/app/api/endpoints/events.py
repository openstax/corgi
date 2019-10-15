from typing import List

from app.db.session import db_session
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db.schema import Events as EventsTable
from app.data_models.models import EventBase, EventCreate, Event
from app.db.utils import get_db

router = APIRouter()


@router.get("/", response_model=List[Event])
async def list_events(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
):
    """List events"""
    events = db_session.query(EventsTable).offset(skip).limit(limit).all()
    return events


@router.post("/", response_model=Event)
async def create_event(
        *,
        db: Session = Depends(get_db),
        event_in: EventCreate
):
    """Create new event"""
    in_data = jsonable_encoder(event_in)
    event = EventsTable(**in_data)
    db_session.add(event)
    db_session.commit()
    return event
