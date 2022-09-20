from datetime import datetime, timezone
from typing import List, Optional

from fastapi import Request, HTTPException, status, Depends
from app.core.config import ADMIN_TEAMS


class UserSession:
    def __init__(self, id_: str, token: str, role: str):
        self.id = id_
        self.token = token
        self.role = role


def active_user(request: Request) -> UserSession:
    should_fail = False
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
    return UserSession(user["github_id"], user["token"], user["role"])


class RequiresRole:
    def __init__(self, role_id: str) -> None:
        self.role_id = role_id

    def __call__(self, user_session: UserSession = Depends(active_user)):
        if user_session.role != self.role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )


async def get_user_teams(client, user):
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
                                 json={"query": body})
    response.raise_for_status()

    user_teams = [
        node["node"]["name"]
        for node in response.json()["data"]["organization"]["teams"]["edges"]
    ]

    return user_teams


def get_user_role(user_teams: List[str]) -> Optional[str]:
    if len(user_teams) == 0:
        role = None
    else:
        role = "basic" # default role for members of any OS teams
        if any(team in user_teams for team in ADMIN_TEAMS):
            role = "admin"
    return role
