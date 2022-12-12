from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import HTTPStatusError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import api_router
from app.core import config
from app.core.errors import CustomBaseError
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
        allow_headers=["*"])

# OAUTH
server.add_middleware(
    SessionMiddleware,
    secret_key=config.SESSION_SECRET,
    max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    same_site='strict',
    https_only=not config.IS_DEV_ENV)

server.add_middleware(DBSessionMiddleware)


@server.exception_handler(HTTPStatusError)
async def unauthorized_exception_handler(
        request: Request,
        exc: HTTPStatusError):
    status_code = exc.response.status_code
    if status_code == 401 or status_code == 403:
        del request.session["user"]
        return JSONResponse(status_code=status_code)


@server.exception_handler(CustomBaseError)
async def custom_base_error_handler(_: Request, cbe: CustomBaseError):
    return JSONResponse(status_code=500, content={"detail": str(cbe)})
