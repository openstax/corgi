from base64 import b64decode, b64encode
from datetime import datetime, timedelta, timezone
from typing import List, Optional, cast

from app.core.config import (ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_TEAMS,
                             SESSION_SECRET)
from app.data_models.models import Role, UserSession
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Request, status


COOKIE_NAME = "user"


class Crypto:
    """Simple delegate class to simplify to encrypting/decrypting strings"""
    f = Fernet(b64encode(b64decode(cast(str, SESSION_SECRET))[:32]))

    @staticmethod
    def encrypt(msg: str, encoding: str = "utf-8") -> str:
        return Crypto.f.encrypt(msg.encode(encoding)).decode(encoding)

    @staticmethod
    def decrypt(msg: str, encoding: str = "utf-8") -> str:
        return Crypto.f.decrypt(msg.encode(encoding)).decode(encoding)


def set_user_session_cookie(request: Request, user: UserSession):
    expiration = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    request.session[COOKIE_NAME] = {
        "exp": expiration.timestamp(),
        "session": Crypto.encrypt(user.json())
    }


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
        user = session.get(COOKIE_NAME, None)
    if user is None or user["exp"] <= datetime.now(timezone.utc).timestamp():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in"
        )
    return UserSession.parse_raw(Crypto.decrypt(user["session"]))


class RequiresRole:
    def __init__(self, role: Role) -> None:
        self.role: int = role.value

    def __call__(self, user_session: UserSession = Depends(active_user)):
        if user_session.role < self.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )
