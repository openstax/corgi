from fastapi import APIRouter

from app.core.config import DEPLOYED_AT, REVISION, STACK_NAME, TAG

router = APIRouter()


@router.get("/")
async def version():  # pragma: no cover
    return {
        "stack_name": STACK_NAME,
        "tag": TAG,
        "revision": REVISION,
        "deployed_at": DEPLOYED_AT,
    }
