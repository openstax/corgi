import os
from datetime import datetime, timedelta, timezone

from urllib.parse import parse_qs
from httpx import AsyncClient
from fastapi import Depends, Request, APIRouter
from fastapi.responses import RedirectResponse
from jose import jwt
from app.auth.utils import UnauthorizedException, UserSession, active_user
from app.auth.config import (SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,
                             GITHUB_LOGIN_URL, CLIENT_ID, CLIENT_SECRET,
                             ADMIN_TEAMS)


router = APIRouter()

@router.get("/login")
async def login():
    return RedirectResponse(url=GITHUB_LOGIN_URL)


@router.get("/callback")
async def callback(code: str = ""):
    async with AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token?"
            f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}"
        )
        response.raise_for_status()
        values = parse_qs(response.text)
        if ("access_token" not in values): raise UnauthorizedException()
        token = values["access_token"][0]

        headers = {
            "Accept":"application/vnd.github+json",
            "Authorization": f"Bearer {token}"
        }

        response = await client.get(f"https://api.github.com/user",
                                    headers=headers)
        response.raise_for_status()
        json = response.json()
        user = json["login"]
        avatar = json["avatar_url"]
        id_ = json["id"]
        body = '''query {
                    organization(login: "openstax") {
                        teams(first: 100, userLogins: ["''' + user + '''"]) {
                        totalCount
                        edges {
                            node {
                                name
                                description
                                }
                            }
                        }
                    }
                }'''
        
        response = await client.post(f"https://api.github.com/graphql",
                                     headers=headers, json={"query": body})
        response.raise_for_status()

    user_teams = [
        node["node"]["name"]
        for node in response.json()["data"]["organization"]["teams"]["edges"]
    ]

    if len(user_teams) == 0:
        raise UnauthorizedException()

    role = "basic"
    if any(team in user_teams for team in ADMIN_TEAMS):
        role = "admin"

    expiration = datetime.now(timezone.utc) + \
                 timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        "token": token,
        "exp": expiration,
        "role": role,
        "github_id": id_
    }
    jwt_encrypted = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    response = RedirectResponse(url=f"/success")
    response.set_cookie(key="authorization", value=jwt_encrypted, secure=True,
                        httponly=True, samesite="lax",
                        expires=ACCESS_TOKEN_EXPIRE_MINUTES*60)
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


@router.get("/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie(key="authorization")
    return response