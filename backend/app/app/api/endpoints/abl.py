from app.db.utils import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.service.abl import get_abl_info_database, add_new_entries
from fastapi import APIRouter
from app.core.auth import active_user
from app.data_models.models import (
    UserSession,
    RequestApproveBook,
    ResponseApprovedBook,
)
from app.github import github_client
from typing import List, Optional

router = APIRouter()


@router.get("/", response_model=List[ResponseApprovedBook])
async def get_abl_info(
    db: Session = Depends(get_db),
    consumer: Optional[str] = None,
    repo_name: Optional[str] = None,
    version: Optional[str] = None,
    code_version: Optional[str] = None
):
    return get_abl_info_database(db, consumer, repo_name, version, code_version)


@router.post("/")
async def add_to_abl(
    *,
    db: Session = Depends(get_db),
    info: List[RequestApproveBook],
    user: UserSession = Depends(active_user)
):
    # Creates a new ApprovedCommit
    # Fetches rex-web books.config.json
    # Removes extraneous ApprovedCommit entries (keeps any version that appears in rex-web and new version)
    # Creates new ABL
    # Pushes new ABL
    async with github_client(user) as client:
        return await add_new_entries(db, info, client)
