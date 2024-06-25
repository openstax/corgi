from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import RequiresRole, active_user
from app.data_models.models import (
    ApprovedBook,
    RequestApproveBooks,
    Role,
    UserSession,
)
from app.db.utils import get_db
from app.github.client import github_client
from app.service.abl import add_to_abl, get_abl_info_database

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
async def add_to_abl_request(
    *,
    user: UserSession = Depends(active_user),
    db: Session = Depends(get_db),
    info: RequestApproveBooks,
):
    # Creates a new ApprovedBook
    # Fetches rex-web release.json
    # Removes extraneous ApprovedBook entries for rex-web
    #   keeps any version that appears in rex-web
    # keeps newest version
    async with github_client(user) as client:
        return await add_to_abl(client, db, info)
