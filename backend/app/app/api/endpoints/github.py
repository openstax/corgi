from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.schema import UserRepository
from app.service.github import RepositoryPermission as DBRepositoryPermission
from app.auth.utils import Role, UserSession, active_user
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
