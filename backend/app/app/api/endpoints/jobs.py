from datetime import datetime, timedelta, timezone
from functools import update_wrapper
from typing import List, Optional

from app.core.auth import RequiresRole, active_user
from app.data_models.models import (Job, JobCreate, JobMin, JobUpdate, Role,
                                    UserSession)
from app.db.utils import get_db
from app.github import github_client
from app.service.jobs import jobs_service
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

router = APIRouter()


def cache(skip_args=0):
    def decorating_function(func):
        last_hash = None
        last_result = None

        def wrapper(*args):
            nonlocal last_hash, last_result
            h = hash(tuple(hash(arg) for arg in args[skip_args:]))
            if h != last_hash:
                last_result = func(*args)
                last_hash = h
            return last_result
        return update_wrapper(wrapper, func)
    return decorating_function


@cache(skip_args=1)
def get_old_jobs_json(db: Session, start: datetime,
                      end: datetime, _: bool):
    return ','.join(Job.from_orm(j).json()
                    for j in jobs_service.get_jobs_in_date_range(
                        db, start, end))

@router.get("/", dependencies=[Depends(RequiresRole(Role.USER))])
def list_jobs(
    db: Session = Depends(get_db),
    range_start: Optional[float] = None,
    clear_cache: bool = False,
):
    """List jobs from time range start till now, up to a maximum of one year trailing"""
    now = datetime.now(timezone.utc)
    if range_start is None:
        yesterday = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            tzinfo=timezone.utc) - timedelta(days=1)
        # Try to get old jobs from cache and then concatenate jobs from today
        old_jobs = get_old_jobs_json(
            db,
            yesterday - timedelta(days=364),
            yesterday,
            clear_cache)
        new_jobs = ",".join([
                Job.from_orm(j).json()
                for j in jobs_service.get_jobs_in_date_range(db, yesterday, now)])

        # Only include lists that have at least 1 job
        joined_jobs = ",".join(jobs for jobs in (old_jobs, new_jobs) if jobs)

        return Response(content=f"[{joined_jobs}]", media_type='application/json')
    else:
        return [Job.from_orm(j) for j in  jobs_service.get_jobs_in_date_range(
            db,
            datetime.fromtimestamp(range_start),
            now
        )]

# rewrite the above endpoint to not use a query param
# and instead use a path param

# @router.get("/", dependencies=[Depends(RequiresRole(Role.USER))])
# def list_jobs(db: Session = Depends(get_db), clear_cache: bool = False):
#     """List all jobs for this year"""
#     now = datetime.now(timezone.utc)
#     yesterday = datetime(
#         year=now.year,
#         month=now.month,
#         day=now.day,
#         tzinfo=timezone.utc) - timedelta(days=1)
#     # Try to get old jobs from cache and then concatenate jobs from today
#     old_jobs = get_old_jobs_json(
#         db,
#         yesterday - timedelta(days=364),
#         yesterday,
#         clear_cache)
#     new_jobs = ",".join([
#             Job.from_orm(j).json()
#             for j in jobs_service.get_jobs_in_date_range(db, yesterday, now)])

#     # Only include lists that have at least 1 job
#     joined_jobs = ",".join(jobs for jobs in (old_jobs, new_jobs) if jobs)

#     return Response(content=f"[{joined_jobs}]", media_type='application/json')


@router.get("/pages/{page}", response_model=List[Job],
            dependencies=[Depends(RequiresRole(Role.USER))])
def list_job_page(
        db: Session = Depends(get_db),
        page: int = 0,
        limit: int = 50):
    """List jobs by page"""
    skip = page * limit
    order_by = jobs_service.schema_model.created_at.desc()
    jobs = jobs_service.get_items_order_by(db,
                                           skip=skip,
                                           limit=limit,
                                           order_by=[order_by])
    return jobs


@router.get("/check", response_model=List[JobMin])
def check(
        job_type_id: Optional[str] = None,
        status_id: Optional[str] = None,
        db: Session = Depends(get_db)):
    filter_by = {}
    if job_type_id is not None:
        filter_by["job_type_id"] = job_type_id
    if status_id is not None:
        filter_by["status_id"] = status_id
    return list(jobs_service.get_items_by(db, limit=20, **filter_by))


@router.get("/{id}", response_model=Job)
def get_job(
        *,
        db: Session = Depends(get_db),
        id: int):
    """Get a single job"""
    job = jobs_service.get(db, id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=Job,
             dependencies=[Depends(RequiresRole(Role.USER))])
async def create_job(
        *,
        db: Session = Depends(get_db),
        user: UserSession = Depends(active_user),
        job_in: JobCreate):
    """Create new job"""
    async with github_client(user) as client:
        job = await jobs_service.create(client, db, job_in, user)
        return job


@router.put("/{id}", response_model=Job)
def update_job(
        *,
        db: Session = Depends(get_db),
        id: int,
        job_in: JobUpdate):
    """Update an existing job"""
    job = jobs_service.get(db_session=db, obj_id=id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # If current job status is completed state
    if int(job.status_id) in [4, 5, 6]:
        # Pipelines will try to override an completed state with
        # assigned, processing status if unlucky
        # Only allow updating to completed states to prevent this
        # Don't raise HTTPException since other fields are likely valid
        incoming_status = int(job_in.status_id)
        job_in.status_id = str(incoming_status if incoming_status in [4, 5, 6]
                               else job.status_id)
    job = jobs_service.update(db, job, job_in)
    return job


@router.get("/error/{id}", dependencies=[Depends(RequiresRole(Role.USER))])
def get_error(
        *,
        db: Session = Depends(get_db),
        id: int):
    job = jobs_service.get(db_session=db, obj_id=id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.error_message
