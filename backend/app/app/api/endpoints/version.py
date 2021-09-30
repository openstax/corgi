from fastapi import APIRouter

from app.core.config import STACK_NAME, REVISION, TAG

router = APIRouter()


@router.get("/")
async def version():
    return {"stack_name": STACK_NAME, "tag": TAG, "revision": REVISION}
