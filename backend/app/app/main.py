from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import api_router
from app.core import config
from app.middleware import DBSessionMiddleware

server = FastAPI(title="CORGI - Content Output Review and Generation Interface")

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
    )

# OAUTH
server.add_middleware(
    SessionMiddleware,
    secret_key=config.SESSION_SECRET,
    max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
)

server.add_middleware(DBSessionMiddleware)
