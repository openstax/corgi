
import logging

import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from app.middleware import DBSessionMiddleware


def homepage(request):
    return PlainTextResponse("CORGI")


def exc(request):
    raise Exception("A CORGI exception has occurred")


app = Starlette(
    routes=[
        Route("/", endpoint=homepage),
        Route("/exc", endpoint=exc),
    ],
    middleware=[Middleware(DBSessionMiddleware)],
)

@pytest.mark.unit
@pytest.mark.nondestructive
def test_db_session_middleware(caplog):
    # GIVEN: A test client and capture log set to DEBUG
    caplog.set_level(logging.DEBUG)
    testclient = TestClient(app)

    # WHEN: A request is made to the homepage
    response = testclient.get("/")

    # THEN: A response code 200 is returned and database messages are logged
    assert response.status_code == 200
    assert "Closing Database session" in caplog.text
    assert "Creating Database session" in caplog.text

    # AND WHEN: A request is made to a route that raises an Exception
    caplog.set_level(logging.INFO)
    response = testclient.get("/exc")

    # THEN: A response 500 code is returned and the exception is logged
    assert response.status_code == 500
    assert "Exception: A CORGI exception has occurred" in caplog.text
    