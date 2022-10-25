from datetime import datetime, timedelta, timezone

from app.core.auth import RequiresRole, active_user
from app.core.config import (ACCESS_TOKEN_EXPIRE_MINUTES, CLIENT_ID,
                             CLIENT_SECRET)
from app.data_models.models import Role, UserSession
from app.db.utils import get_db
from app.github.api import (AccessDeniedException, AuthenticationException,
                            authenticate_user)
from app.github.utils import sync_user_data
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session


router = APIRouter()

oauth = OAuth()
oauth.register(
    "github",
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    scope="read:user repo",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)


if oauth.github is None:
    raise Exception("BUG: GitHub oauth could not be registered")


github_oauth = oauth.github


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await github_oauth.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request, code: str = "",
                   db: Session = Depends(get_db)):
    try:
        user = await authenticate_user(db, code, sync_user_data)
        expiration = datetime.now(timezone.utc) + \
                     timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        request.session["user"] = {
            "exp": expiration.timestamp(),
            "session": user.json()
        }

        response = RedirectResponse(url=f"/")
        return response
    except AuthenticationException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Could not authenticate'
        )
    except AccessDeniedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden'
        )


@router.get("/success")
async def success(
    active_user: UserSession = Depends(active_user)
):
    return active_user.json()


@router.get("/admin-example", dependencies=[Depends(RequiresRole(Role.ADMIN))])
async def get_admin_info():
    return "Congrats! You're an admin."
