import asyncio
import sys
from pathlib import Path
from typing import cast
import shutil

import vcr
from app.github import (AuthenticatedClient, get_book_repository,
                        get_collections, get_user, get_user_repositories,
                        get_user_teams)
from httpx import AsyncClient


def apply_key_whitelist(d, whitelist):
    whitelist = [k.lower() for k in whitelist]
    for key in list(d.keys()):
        if key.lower() not in whitelist:
            del d[key]


class BaseSanitizer:
    """Delete potentially sensitive data"""

    def __init__(self, vcr) -> None:
        self.vcr = vcr

    def transform(self, d):
        request_headers = d["interactions"][0]["request"]["headers"]
        response_headers = d["interactions"][0]["response"]["headers"]
        for headers, whitelist in (
                (request_headers, ("host",)),
                (response_headers, ("content-type", "server"))):
            apply_key_whitelist(headers, whitelist)

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
        # Keep exactly what is used by the backend, delete extra data
        apply_key_whitelist(body, ("login", "avatar_url", "id"))
        # HACK: Set the content to save from the response
        d["interactions"][0]["response"]["content"] = json.dumps(body)


DATA_DIR = str(Path(__file__).parent / "data")
my_vcr = vcr.VCR(cassette_library_dir=DATA_DIR)


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


async def async_main(access_token: str):
    async with AsyncClient() as client:
        client.headers = {"authorization": f"Bearer {access_token}"}
        client = cast(AuthenticatedClient, client)
        user = await mock_get_user(client, access_token)
        await mock_get_user_teams(client, user.name)
        await mock_get_user_repositories(
            client, "org:openstax osbooks in:name is:public")
        await mock_get_book_repository(client, "tiny-book", "openstax", "main")
        await mock_get_collections(client, "tiny-book", "openstax", "main")


def main(access_token):
    shutil.rmtree(DATA_DIR)
    asyncio.run(async_main(access_token))


if __name__ == "__main__":
    access_token = sys.argv[1]
    main(access_token)
