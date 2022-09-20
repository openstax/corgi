import imp
from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core import config
from app.middleware import DBSessionMiddleware
from app.auth.utils import UnauthorizedException

server = FastAPI(title="COPS - Content Output Producer Service")

# Add API endpoints
server.include_router(api_router, prefix="/api")

# CORS
origins = []

# Set all CORS enabled origins
if config.BACKEND_CORS_ORIGINS:
    origins_raw = config.BACKEND_CORS_ORIGINS.split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    server.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),

server.add_middleware(DBSessionMiddleware)

@server.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return Response(status_code=401)