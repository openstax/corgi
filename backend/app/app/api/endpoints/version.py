from enum import Enum

from fastapi import APIRouter, Depends

from app.api.utils import async_memoize_timed
from app.core.auth import RequiresRole
from app.core.config import DEPLOYED_AT, REVISION, STACK_NAME, TAG
from app.data_models.models import Role
from app.service.docker_hub import api


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


@async_memoize_timed(ttl=5 * 60)
async def get_tags(repo: str, count: int, pattern: str):
    return await api.get_newest_tags(repo, count, {"pattern": pattern})


@router.get("/tags/{repo}", dependencies=[Depends(RequiresRole(Role.USER))])
async def get_tags_request(
    repo: AllowedRepo, count: int = 5, pattern: str = r"^\d+\.\d+$"
):
    repo_compiled = repo.replace("::", "/")
    count = min(count, 25)
    items = await get_tags(repo_compiled, count, pattern)
    current_version = next((i for i in items if i == TAG), None)
    count = len(items)
    return {"items": items, "count": count, "current_version": current_version}
