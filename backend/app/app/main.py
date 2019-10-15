from fastapi import FastAPI
from starlette.requests import Request

from app.db.session import db_session
from app.api import api_router

server = FastAPI()

server.include_router(api_router, prefix="/api")


@server.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = db_session
    response = await call_next(request)
    request.state.db.remove()
    return response
