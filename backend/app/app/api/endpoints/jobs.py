from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.service.jobs import jobs_service
from app.data_models.models import JobCreate, JobUpdate, Job
from app.db.utils import get_db

router = APIRouter()


@router.get("/", response_model=List[Job])
def list_jobs(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
):
    """List jobs"""
    jobs = jobs_service.get_items(db, skip=skip, limit=limit)
    return jobs


@router.get("/{id}", response_model=Job)
def get_job(
        *,
        db: Session = Depends(get_db),
        id: int
):
    """Get a single job"""
    job = jobs_service.get(db, id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=Job)
def create_job(
        *,
        db: Session = Depends(get_db),
        job_in: JobCreate
):
    """Create new job"""
    job = jobs_service.create(db, job_in)
    return job


@router.put("/{id}", response_model=Job)
def update_job(
        *,
        db: Session = Depends(get_db),
        id: int,
        job_in: JobUpdate
):
    """Update an existing job"""
    job = jobs_service.get(db_session=db, obj_id=id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs_service.update(db, job, job_in)
    return job
