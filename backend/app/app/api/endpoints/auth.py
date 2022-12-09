import logging
from typing import Awaitable
from datetime import datetime, timedelta, timezone

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, IS_DEV_ENV
from app.data_models.models import UserSession
from app.db.utils import get_db
from app.github import (AccessDeniedError, authenticate_client, get_user,
                        github_oauth, sync_user_data)
from app.core.errors import CustomBaseError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from httpx import AsyncClient
from sqlalchemy.orm import Session
from starlette.datastructures import URL

router = APIRouter()


def set_user_session_cookie(request: Request, user: UserSession):
    expiration = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    request.session["user"] = {
        "exp": expiration.timestamp(),
        "session": user.json()
    }


async def handle_auth_errors(thunk: Awaitable):
    try:
        return await thunk
    except AccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
    except CustomBaseError:
        raise
    except Exception as e:
        logging.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not authenticate"
        )


async def authenticate_token_user(request: Request, token: str):
    async with AsyncClient() as client:
        client = authenticate_client(client, token)
        user = await get_user(client, token)
        set_user_session_cookie(request, user)


async def authenticate_user(request: Request, db: Session):
    values = await github_oauth.authorize_access_token(request)
    token = values["access_token"]
    async with AsyncClient() as client:
        client = authenticate_client(client, token)
        user = await get_user(client, token)
        await sync_user_data(client, db, user)
    return user


@router.get("/token-login")
async def token_login(request: Request):
    access_token = request.headers.get("authorization", None)
    if access_token is not None:
        token = access_token.split(" ")[1]
        return await handle_auth_errors(authenticate_token_user(request, token))
    else:
        raise CustomBaseError("Missing required token")


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    if not IS_DEV_ENV:  # pragma: no cover
        redirect_uri = str(URL(redirect_uri).replace(scheme="https"))
    return await github_oauth.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    user = await handle_auth_errors(authenticate_user(request, db))
    set_user_session_cookie(request, user)

    response = RedirectResponse(url=f"/")
    return response
