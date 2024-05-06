import logging
from typing import Awaitable

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from httpx import AsyncClient
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from app.core.auth import set_user_session_cookie
from app.core.config import IS_DEV_ENV
from app.core.errors import CustomBaseError
from app.db.utils import get_db
from app.github import (
    AccessDeniedError,
    authenticate_client,
    get_user,
    github_oauth,
    sync_user_repositories,
)
from app.service.user import user_service

router = APIRouter()


class AuthenticationError(Exception):
    def __init__(self):
        super().__init__("Could not authenticate")


async def handle_auth_errors(thunk: Awaitable):
    try:
        return await thunk
    except AccessDeniedError as ade:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
        ) from ade
    except CustomBaseError:
        raise
    except Exception as e:
        logging.error(e)
        raise AuthenticationError() from e


async def authenticate_token_user(request: Request, token: str, db: Session):
    async with AsyncClient() as client:
        client = authenticate_client(client, token)
        user = await get_user(client, token)
        user_service.upsert_user(db, user)
        set_user_session_cookie(request, user)


async def authenticate_user(request: Request, db: Session):
    values = await github_oauth.authorize_access_token(request)
    token = values["access_token"]
    async with AsyncClient() as client:
        client = authenticate_client(client, token)
        user = await get_user(client, token)
        user_service.upsert_user(db, user)
        await sync_user_repositories(client, db, user)
    return user


@router.get("/token-login")
async def token_login(request: Request, db: Session = Depends(get_db)):
    access_token = request.headers.get("authorization", None)
    if access_token is not None:
        token = access_token.split("Bearer ")[1]
        return await handle_auth_errors(
            authenticate_token_user(request, token, db)
        )
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
    try:
        user = await handle_auth_errors(authenticate_user(request, db))
    except AuthenticationError:
        return RedirectResponse(url="/errors/auth-error")

    set_user_session_cookie(request, user)

    response = RedirectResponse(url="/")
    return response
