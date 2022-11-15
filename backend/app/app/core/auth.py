from datetime import datetime, timezone
from typing import List, Optional

from app.core.config import ADMIN_TEAMS
from app.data_models.models import Role, UserSession
from fastapi import Depends, HTTPException, Request, status


def get_user_role(user_teams: List[str]) -> Optional[Role]:
    if len(user_teams) == 0:
        role = None
    else:
        role = Role.DEFAULT
        if any(team in user_teams for team in ADMIN_TEAMS):
            role = Role.ADMIN
    return role


def active_user(request: Request) -> UserSession:
    session = request.session
    user = None
    if session is not None:
        user = session.get("user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in"
        )
    if user["exp"] <= datetime.now(timezone.utc).timestamp():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in"
        )
    return UserSession.parse_raw(user["session"])


class RequiresRole:
    def __init__(self, role: Role) -> None:
        self.role: int = role.value

    def __call__(self, user_session: UserSession = Depends(active_user)):
        if user_session.role < self.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )
