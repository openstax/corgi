import pytest
from starlette.testclient import TestClient

from app.main import server

@pytest.fixture(scope="session")
def testclient():
    client = TestClient(server)
    yield client
