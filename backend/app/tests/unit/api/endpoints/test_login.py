from app.github.api import AccessDeniedException, AuthenticationException
import pytest
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


@pytest.mark.unit
@pytest.mark.nondestructive
def test_login_success(testclient, mock_login_success):
    response = testclient.get(f"/api/auth/login", allow_redirects=False)
    assert response.status_code == 307
    redirect_location = response.headers.get("location")
    assert redirect_location is not None
    response = testclient.get(redirect_location, allow_redirects=False)
    assert response.status_code == 307
    cookie = response.headers.get("set-cookie")
    assert cookie is not None
    assert "session=" in cookie
    assert str(ACCESS_TOKEN_EXPIRE_MINUTES * 60) in cookie


def get_mock_authenticate(exc):
    async def mock_authenticate(*_):
        raise exc
    return mock_authenticate


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "mock_authenticate,status_code,text",
    [(get_mock_authenticate(AccessDeniedException), 403, "Forbidden"),
     (get_mock_authenticate(AuthenticationException), 500,
                            "Could not authenticate")]
)
def test_login_exception(testclient, monkeypatch, mock_authenticate,
                         status_code, text):
    monkeypatch.setattr("app.api.endpoints.auth.authenticate_user",
                        mock_authenticate)

    response = testclient.get("/api/auth/callback", allow_redirects=False)
    assert response.status_code == status_code
    assert response.json()["detail"] == text