import pytest
from app.main import server
from fastapi.responses import RedirectResponse
from starlette.testclient import TestClient


@pytest.fixture
def mock_oauth_redirect(monkeypatch):
    class MockOAuth:
            async def authorize_redirect(self, request, redirect_uri):
                return RedirectResponse(redirect_uri)
    
    monkeypatch.setattr("app.api.endpoints.auth.github_oauth", MockOAuth())


@pytest.fixture
def mock_login_success(monkeypatch, mock_oauth_redirect):
    async def mock_authenticate(db, code, callback):
        from app.data_models.models import Role, UserSession
        return UserSession(id=1, token="abc", role=Role.ADMIN, name="Test",
                           avatar_url="http://example.com")

    monkeypatch.setattr("app.api.endpoints.auth.authenticate_user",
                        mock_authenticate)



@pytest.fixture(scope="session")
def testclient():
    client = TestClient(server)
    yield client
