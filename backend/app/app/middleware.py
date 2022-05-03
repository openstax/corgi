import logging

from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import Session


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logging.debug(f"Creating Database session for {request.url}")
        response = Response("Internal server error", status_code=500)
        # https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-middleware
        try: 
            request.state.db = Session()
            response = await call_next(request)
        # We log the exception because it could be one of many.
        except Exception(e):
            logging.exception(e)
        # Always close the db session, even after an exception
        finally:
            logging.debug(f"Closing Database session for {request.url}")
            request.state.db.close()
        return response
