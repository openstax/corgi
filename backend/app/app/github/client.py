from contextlib import asynccontextmanager
from typing import cast

from httpx import AsyncClient

from app.data_models.models import UserSession


class AuthenticatedClient(AsyncClient):
    pass


def authenticate_client(client: AsyncClient, token: str) -> AuthenticatedClient:
    client.headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    return cast(AuthenticatedClient, client)


@asynccontextmanager
async def github_client(user: UserSession):  # pragma: no cover
    async with AsyncClient() as client:
        yield authenticate_client(client, user.token)
