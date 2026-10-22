import asyncio
import os
import shutil
import sys
from pathlib import Path
from typing import cast

import vcr
from httpx import AsyncClient
from vcr.record_mode import RecordMode

import app.core.config as config
from app.github import (
    AuthenticatedClient,
    get_book_repository,
    get_collections,
    get_file_content,
    get_user,
    get_user_repositories,
    get_user_teams,
)

vcr_args = {
    "record_mode": RecordMode.NEW_EPISODES
    if os.getenv("VCR_RECORD") == "1"
    else RecordMode.NONE
}


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
        for interaction in d["interactions"]:
            request_headers = interaction["request"]["headers"]
            response_headers = interaction["response"]["headers"]
            for headers, whitelist in (
                (request_headers, ("host",)),
                (response_headers, ("content-type", "server")),
            ):
                apply_key_whitelist(headers, whitelist)

    def serialize(self, d, *args, **kwargs):
        self.transform(d)
        return self.vcr.serializers[my_vcr.serializer].serialize(
            d, *args, **kwargs
        )

    def deserialize(self, *args, **kwargs):
        return self.vcr.serializers[my_vcr.serializer].deserialize(
            *args, **kwargs
        )


class UserSanitizer(BaseSanitizer):
    """Delete potentially sensitive user data"""

    def transform(self, d):
        import json

        super().transform(d)
        for interaction in d["interactions"]:
            body = json.loads(interaction["response"]["content"])
            # Keep exactly what is used by the backend, delete extra data
            apply_key_whitelist(body, ("login", "avatar_url", "id"))
            # HACK: Set the content to save from the response
            interaction["response"]["content"] = json.dumps(body)


DATA_DIR = str(Path(__file__).parent / "data")
my_vcr = vcr.VCR(cassette_library_dir=DATA_DIR)


my_vcr.register_serializer("base_sanitizer", BaseSanitizer(my_vcr))
my_vcr.register_serializer("user_sanitizer", UserSanitizer(my_vcr))


@my_vcr.use_cassette("get_user.yaml", serializer="user_sanitizer", **vcr_args)
async def mock_get_user(client, access_token):
    return await get_user(client, access_token)


@my_vcr.use_cassette(
    "get_user_teams.yaml", serializer="base_sanitizer", **vcr_args
)
async def mock_get_user_teams(client, user):
    import app.github.api

    app.github.api.IS_DEV_ENV = False
    teams = await get_user_teams(client, user)
    app.github.api.IS_DEV_ENV = True
    return teams


@my_vcr.use_cassette(
    "get_user_repositories.yaml", serializer="base_sanitizer", **vcr_args
)
async def mock_get_user_repositories(client, query):
    return await get_user_repositories(client, query)


@my_vcr.use_cassette(
    "get_book_repository.yaml", serializer="base_sanitizer", **vcr_args
)
async def mock_get_book_repository(client, repo_name, repo_owner, version):
    return await get_book_repository(client, repo_name, repo_owner, version)


@my_vcr.use_cassette(
    "get_collections.yaml", serializer="base_sanitizer", **vcr_args
)
async def mock_get_collections(client, repo_name, repo_owner, commit_sha):
    return await get_collections(client, repo_name, repo_owner, commit_sha)


@my_vcr.use_cassette(
    "get_file_content.yaml", serializer="base_sanitizer", **vcr_args
)
async def mock_get_file_content(client, owner, repo, path, ref=None):
    return await get_file_content(client, owner, repo, path, ref)


async def async_main(access_token: str):
    async with AsyncClient() as client:
        client.headers = {"authorization": f"Bearer {access_token}"}
        client = cast(AuthenticatedClient, client)
        user = await mock_get_user(client, access_token)
        await mock_get_user_teams(client, user.name)
        await mock_get_user_repositories(
            client, "org:openstax osbooks in:name is:public"
        )
        await mock_get_book_repository(client, "tiny-book", "openstax", "main")
        await mock_get_collections(client, "tiny-book", "openstax", "main")
        await mock_get_file_content(
            client, *config.REX_WEB_ARCHIVE_CONFIG.split(":", 2)
        )


def main(access_token):
    shutil.rmtree(DATA_DIR)
    asyncio.run(async_main(access_token))


if __name__ == "__main__":
    access_token = sys.argv[1]
    main(access_token)
