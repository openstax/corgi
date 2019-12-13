from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.service.event import event_service
from app.data_models.models import EventCreate, EventUpdate, Event
from app.db.utils import get_db

router = APIRouter()


@router.get("/", response_model=List[Event])
async def list_events(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
):
    """List events"""
    events = event_service.get_items(db, skip=skip, limit=limit)
    return events


@router.get("/{id}", response_model=Event)
async def get_event(
        *,
        db: Session = Depends(get_db),
        id: int
):
    """Get a single event"""
    event = event_service.get(db, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=Event)
async def create_event(
        *,
        db: Session = Depends(get_db),
        event_in: EventCreate
):
    """Create new event"""
    event = event_service.create(db, event_in)
    return event


@router.put("/{id}", response_model=Event)
async def update_event(
        *,
        db: Session = Depends(get_db),
        id: int,
        event_in: EventUpdate
):
    """Update an existing event"""
    event = event_service.get(db_session=db, obj_id=id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event = event_service.update(db, event, event_in)
    return event
