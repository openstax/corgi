import asyncio
import json
import sys
from time import strftime

from httpx import AsyncClient


async def create_entries(client, jobs, code_version):
    assert len(jobs) > 0, "Create some jobs first"
    job = jobs[0]
    books = job["books"]
    entries = [
        {
            "uuid": book["uuid"],
            "commit_sha": job["version"],
            "code_version": code_version,
            "consumer": "REX",
        }
        for book in books
    ]
    response = await client.post(
        "http://localhost/api/abl/", data=json.dumps(entries)
    )
    response.raise_for_status()
    return entries


async def check_entries(client, entries, code_version):
    response = await client.get("http://localhost/api/abl/")
    response.raise_for_status()
    fetched_entries = response.json()
    filtered = [
        entry["uuid"] == entries[0]["uuid"]
        and entry["code_version"] == code_version
        for entry in fetched_entries
    ]
    assert len(filtered) == len(entries), "Failed to add ABL entry"


async def authenticate_client(client, token):
    response = await client.get(
        "http://localhost/api/auth/token-login",
        headers={"Authorization": f"Bearer {token}"},
        follow_redirects=True,
    )
    response.raise_for_status()
    assert (
        response.cookies.get("session", None) is not None
    ), "Could not get session cookie"


async def main():
    token = sys.argv[1]
    async with AsyncClient() as client:
        await authenticate_client(client, token)
        response = await client.get("http://localhost/api/jobs/")
        response.raise_for_status()
        jobs = response.json()
        for i in range(2):
            test_code_version = strftime(f"%Y%m%d.%H%M%S-{i}")
            entries = await create_entries(client, jobs, test_code_version)
            await check_entries(client, entries, test_code_version)


if __name__ == "__main__":
    asyncio.run(main())
