from fastapi import APIRouter

from app.api.endpoints import abl, auth, github, jobs, ping, status, version

api_router = APIRouter()
api_router.include_router(ping.router, prefix="/ping", tags=["ping"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(abl.router, prefix="/abl", tags=["abl"])
api_router.include_router(status.router, prefix="/status", tags=["status"])
api_router.include_router(version.router, prefix="/version", tags=["version"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
