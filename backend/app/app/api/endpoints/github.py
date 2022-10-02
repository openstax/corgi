from typing import List

from app.data_models.models import GitHubRepo
from app.db.schema import Repository, UserRepository
from app.service.github import RepositoryPermission as DBRepositoryPermission
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from httpx import AsyncClient

from app.auth.utils import Role, UserSession, active_user, github_client
from app.db.utils import get_db


router = APIRouter()


@router.get("/repositories")
async def repositories(user: UserSession = Depends(active_user), db: Session = Depends(get_db)):
    query = db.query(UserRepository)
    if user.role != Role.ADMIN:
        query = query.filter(
            UserRepository.user_id == user.id,
            UserRepository.permission_id.in_([
                DBRepositoryPermission.ADMIN,
                DBRepositoryPermission.WRITE
            ])
        )
    else:
        query = query = query.filter(UserRepository.user_id == user.id)
    repos = [ur.repository for ur in query.all()]
    # TODO: Move into a service with a response type
    return [{ "name": r.name, "id": r.id } for r in repos]
