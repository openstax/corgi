from datetime import datetime, timedelta, timezone

from urllib.parse import parse_qs
from app.db.schema import Repository
from httpx import AsyncClient
from fastapi import Depends, Request, APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from app.auth.utils import (RequiresRole, Role, UserSession, active_user,
                            get_user_role, get_user_teams)
from app.core.config import (ACCESS_TOKEN_EXPIRE_MINUTES, CLIENT_ID,
                             CLIENT_SECRET)
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from app.db.utils import get_db
from app.service.github import repository_service, user_service


router = APIRouter()

oauth = OAuth()
oauth.register(
    "github",
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    scope="read:user",
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
async def callback(request: Request, code: str = "", db: Session = Depends(get_db) ):
    async with AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token?"
            f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}"
        )
        response.raise_for_status()
        values = parse_qs(response.text)
        if ("access_token" not in values):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Could not authenticate'
            )
        token = values["access_token"][0]

        client.headers = {
            "Accept":"application/vnd.github+json",
            "Authorization": f"Bearer {token}"
        }

        response = await client.get(f"https://api.github.com/user")
        response.raise_for_status()
        json = response.json()
        name = json["login"]
        avatar_url = json["avatar_url"]
        id_ = json["id"]
        user_teams = await get_user_teams(client, name)
        role = get_user_role(user_teams)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Forbidden'
            )
        user_repos = await repository_service.get_user_repositories(client)
    user = UserSession(
        id=id_,
        token=token,
        role=role,
        avatar_url=avatar_url,
        name=name
    )
    user_service.upsert_user(db, user)
    repository_service.upsert_repositories(db, [
        Repository(id=repo.database_id, name=repo.name, owner="openstax")
        for repo in user_repos
    ])
    repository_service.upsert_user_repositories(db, id_, user_repos)

    expiration = datetime.now(timezone.utc) + \
                 timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    request.session["user"] = {
        "exp": expiration.timestamp(),
        "session": user.json()
    }

    response = RedirectResponse(url=f"/")
    return response

@router.get("/success")
async def success(
    active_user: UserSession = Depends(active_user)
):
    return active_user.json()


@router.get("/failure")
async def failure():
    return ":`<"


@router.get("/admin-example", dependencies=[Depends(RequiresRole(Role.ADMIN))])
async def get_admin_info():
    return "Congrats! You're an admin."
