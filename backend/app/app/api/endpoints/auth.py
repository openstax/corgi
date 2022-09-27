from datetime import datetime, timedelta, timezone

from urllib.parse import parse_qs
from httpx import AsyncClient
from fastapi import Depends, Request, APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from app.auth.utils import (RequiresRole, Role, UserSession, active_user,
                            get_user_role, get_user_teams)
from app.core.config import (ACCESS_TOKEN_EXPIRE_MINUTES, CLIENT_ID,
                             CLIENT_SECRET)
from authlib.integrations.starlette_client import OAuth


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
async def callback(request: Request, code: str = ""):
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
        user = json["login"]
        avatar = json["avatar_url"]
        id_ = json["id"]
    
        user_teams = await get_user_teams(client, user)
    role = get_user_role(user_teams)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden'
        )

    expiration = datetime.now(timezone.utc) + \
                 timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        "token": token,
        "exp": expiration.timestamp(),
        "role": role.value,
        "github_id": id_
    }
    request.session["user"] = data

    response = RedirectResponse(url=f"/")
    return response

@router.get("/success")
async def success(
    request: Request,
    active_user: UserSession = Depends(active_user)
):
    print(active_user.id)
    print(active_user.role)
    return "it worked!"


@router.get("/failure")
async def failure():
    return ":`<"


@router.get("/admin-example", dependencies=[Depends(RequiresRole(Role.ADMIN))])
async def get_admin_info():
    return "Congrats! You're an admin."
