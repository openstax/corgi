from typing import Optional
from datetime import datetime, timezone

from fastapi import Cookie
from app.auth.config import SECRET_KEY, ALGORITHM
from jose import JOSEError, jwt

class UserSession:
    def __init__(self, id_: str, token: str, role: str):
        self.id = id_
        self.token = token
        self.role = role


class UnauthorizedException(Exception):
    pass


def active_user(
    authorization: Optional[str] = Cookie(default=None)
) -> UserSession:
    if authorization is None:
        raise UnauthorizedException()
    try:
        data = jwt.decode(authorization, SECRET_KEY, algorithms=[ALGORITHM])
        if data["exp"] <= datetime.now(timezone.utc).timestamp():
            raise UnauthorizedException()
        return UserSession(data["github_id"], data["token"], data["role"])
    except JOSEError:
        raise UnauthorizedException()
