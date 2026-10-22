import asyncio
from enum import Enum

from fastapi import APIRouter, Depends
from httpx import AsyncClient

from app.api.utils import async_memoize_timed
from app.core.auth import RequiresRole
from app.core.config import DEPLOYED_AT, REVISION, STACK_NAME, TAG
from app.data_models.models import Role
from app.github.api import get_tags
from app.service import docker_hub

_MAX_TAGS_FETCH = 50


class AllowedRepo(str, Enum):
    ENKI = "openstax::enki"


router = APIRouter()


@router.get("/")
async def version():  # pragma: no cover
    return {
        "stack_name": STACK_NAME,
        "tag": TAG,
        "revision": REVISION,
        "deployed_at": DEPLOYED_AT,
    }


async def _get_dockerhub_tags(repo: str, pattern: str) -> set[str]:
    return set(
        await docker_hub.api.get_newest_tags(
            repo, _MAX_TAGS_FETCH, {"pattern": pattern}
        )
    )


async def _get_github_tags(owner: str, repo: str, pattern: str) -> set[str]:
    async with AsyncClient() as client:
        tags = await get_tags(client, owner, repo, _MAX_TAGS_FETCH, pattern)
        return set(tags)


@async_memoize_timed(ttl=5 * 60)
async def _get_tags(
    owner: str, repo: str, pattern: str, count: int
) -> list[str]:
    dh_tags, gh_tags = await asyncio.gather(
        _get_dockerhub_tags(f"{owner}/{repo}", pattern),
        _get_github_tags(owner, repo, pattern),
    )
    return sorted(dh_tags & gh_tags, reverse=True)[:count]


@router.get("/tags/{repo}", dependencies=[Depends(RequiresRole(Role.USER))])
async def get_tags_request(
    repo: AllowedRepo, count: int = 5, pattern: str = r"^\d+\.\d+$"
):
    owner, repo_name = repo.replace("::", "/").split("/", 1)
    count = min(count, 25)
    items = await _get_tags(owner, repo_name, pattern, count)
    return {"items": items, "count": len(items)}
