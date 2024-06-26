from typing import List, Optional

from fastapi import APIRouter, Depends
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.auth import RequiresRole
from app.data_models.models import (
    ApprovedBook,
    RequestApproveBook,
    Role,
)
from app.db.utils import get_db
from app.service.abl import add_new_entries, get_abl_info_database

router = APIRouter()


@router.get("/", response_model=List[ApprovedBook])
async def get_abl_info(
    db: Session = Depends(get_db),
    consumer: Optional[str] = None,
    repo_name: Optional[str] = None,
    version: Optional[str] = None,
    code_version: Optional[str] = None,
):
    return get_abl_info_database(db, consumer, repo_name, version, code_version)


@router.post("/", dependencies=[Depends(RequiresRole(Role.ADMIN))])
async def add_to_abl(
    *,
    db: Session = Depends(get_db),
    info: List[RequestApproveBook],
):
    # Creates a new ApprovedBook
    # Fetches rex-web release.json
    # Removes extraneous ApprovedBook entries for rex-web
    #   keeps any version that appears in rex-web
    # keeps newest version
    async with AsyncClient() as client:
        return await add_new_entries(db, info, client)
