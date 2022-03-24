import pytest
from starlette.testclient import TestClient

from app.main import server

@pytest.fixture
def testclient():
    client = TestClient(server)
    yield client
