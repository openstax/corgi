from fastapi import FastAPI

from app.api import api_router
from app.middleware import DBSessionMiddleware

server = FastAPI()

server.include_router(api_router, prefix="/api")

server.add_middleware(DBSessionMiddleware)
