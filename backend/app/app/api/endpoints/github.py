from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import active_user
from app.data_models.models import RepositorySummary, UserSession
from app.db.utils import get_db
from app.github import get_book_repository
from app.github.client import github_client
from app.service.user import user_service

router = APIRouter()


@router.get("/repository-summary", response_model=List[RepositorySummary])
async def repositories(
    user: UserSession = Depends(active_user), db: Session = Depends(get_db)
):
    return user_service.get_user_repositories(db, user)


@router.get("/book-repository/{owner}/{name}")
async def get_book_repository_endpoint(
    owner: str,
    name: str,
    version: str = Query("main", description="Commit or ref to use"),
    user: UserSession = Depends(active_user),
):
    async with github_client(user) as client:
        return await get_book_repository(client, name, owner, version)
