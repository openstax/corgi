from typing import List

from app.core.auth import active_user
from app.data_models.models import RepositorySummary, UserSession
from app.db.utils import get_db
from app.service.user import user_service
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/repository-summary", response_model=List[RepositorySummary])
async def repositories(
        user: UserSession = Depends(active_user),
        db: Session = Depends(get_db)):
    return user_service.get_user_repositories(db, user)
