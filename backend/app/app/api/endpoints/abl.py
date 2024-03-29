
from app.service.abl import get_abl_info
from fastapi import APIRouter

router = APIRouter()

@router.get("/{repo_name}/{version}")
async def get(repo_name, version):
    return await get_abl_info(repo_name, version)