from datetime import datetime, timedelta, timezone
from app.core.auth import active_user

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, IS_DEV_ENV
from app.data_models.models import UserSession
from app.db.utils import get_db
from app.github import (AccessDeniedException, AuthenticationException,
                        authenticate_user, sync_user_data, github_oauth)
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.datastructures import URL

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    if not IS_DEV_ENV:
        redirect_uri = str(URL(redirect_uri).replace(scheme="https"))
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
