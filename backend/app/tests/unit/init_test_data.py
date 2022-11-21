import asyncio
import sys
from pathlib import Path
from typing import Callable, cast

import vcr
from app.github import (AuthenticatedClient, get_book_repository,
                        get_collections, get_user, get_user_repositories,
                        get_user_teams)
from httpx import AsyncClient


class BaseSanitizer:
    """Delete potentially sensitive data"""

    def __init__(self, vcr) -> None:
        self.vcr = vcr

    def transform(self, d):
        request_headers = d["interactions"][0]["request"]["headers"]
        response_headers = d["interactions"][0]["response"]["headers"]
        for k in ("authorization",):
            del request_headers[k]
        for k in list(response_headers.keys()):
            if k.startswith("X-") or k.startswith("github-"):
                del response_headers[k]

    def serialize(self, d, *args, **kwargs):
        self.transform(d)
        return self.vcr.serializers[my_vcr.serializer].serialize(
            d, *args, **kwargs)

    def deserialize(self, *args, **kwargs):
        return self.vcr.serializers[my_vcr.serializer].deserialize(
            *args, **kwargs)


class UserSanitizer(BaseSanitizer):
    """Delete potentially sensitive user data"""

    def transform(self, d):
        import json
        super().transform(d)
        body = json.loads(d["interactions"][0]["response"]["content"])
        allowed = set(["login", "avatar_url", "id"])
        # Keep exactly what is used by the backend, delete extra data
        for key in set(body.keys()) - allowed:
            del body[key]
        d["interactions"][0]["response"]["content"] = json.dumps(body)


my_vcr = vcr.VCR(cassette_library_dir=str(Path(__file__).parent / "data"))


my_vcr.register_serializer("base_sanitizer", BaseSanitizer(my_vcr))
my_vcr.register_serializer("user_sanitizer", UserSanitizer(my_vcr))


@my_vcr.use_cassette("get_user.yaml", serializer="user_sanitizer")
async def mock_get_user(client, access_token):
    return await get_user(client, access_token)


@my_vcr.use_cassette("get_user_teams.yaml", serializer="base_sanitizer")
async def mock_get_user_teams(client, user):
    import app.github.api
    app.github.api.IS_DEV_ENV = False
    teams = await get_user_teams(client, user)
    app.github.api.IS_DEV_ENV = True
    return teams


@my_vcr.use_cassette("get_user_repositories.yaml", serializer="base_sanitizer")
async def mock_get_user_repositories(client, query):
    return await get_user_repositories(client, query)


@my_vcr.use_cassette("get_book_repository.yaml", serializer="base_sanitizer")
async def mock_get_book_repository(client, repo_name, repo_owner, version):
    return await get_book_repository(client, repo_name, repo_owner, version)


@my_vcr.use_cassette("get_collections.yaml", serializer="base_sanitizer")
async def mock_get_collections(client, repo_name, repo_owner, commit_sha):
    return await get_collections(client, repo_name, repo_owner, commit_sha)


async def main(access_token: str):
    async with AsyncClient() as client:
        client.headers = {"authorization": f"Bearer {access_token}"}
        client = cast(AuthenticatedClient, client)
        user = await mock_get_user(client, access_token)
        await mock_get_user_teams(client, user.name)
        await mock_get_user_repositories(
            client, "org:openstax osbooks in:name is:public")
        await mock_get_book_repository(client, "tiny-book", "openstax", "main")
        await mock_get_collections(client, "tiny-book", "openstax", "main")


if __name__ == "__main__":
    access_token = sys.argv[1]
    asyncio.run(main(access_token))
