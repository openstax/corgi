from typing import List, Optional

from fastapi import APIRouter, Depends
from httpx import AsyncClient
from sqlalchemy.orm import Session

import app.service.abl as abl_service
from app.core.auth import RequiresRole
from app.data_models.models import (
    ApprovedBook,
    RequestApproveBook,
    Role,
)
from app.db.utils import get_db

router = APIRouter()


@router.get("/", response_model=List[ApprovedBook])
async def get_abl_info(
    db: Session = Depends(get_db),
    consumer: Optional[str] = None,
    repo_name: Optional[str] = None,
    version: Optional[str] = None,
    code_version: Optional[str] = None,
):
    return abl_service.get_abl_info_database(
        db, consumer, repo_name, version, code_version
    )


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
        return await abl_service.add_new_entries(db, info, client)


@router.get("/rex-release-version")
async def get_rex_release_version():
    async with AsyncClient() as client:
        version = await abl_service.get_rex_release_version(client)
        return {"version": version}
