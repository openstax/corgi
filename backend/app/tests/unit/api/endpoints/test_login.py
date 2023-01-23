import json
from base64 import b64decode

import pytest
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.errors import CustomBaseError
from app.github.api import AccessDeniedError


def check_cookie_value(cookie):
    from app.core.auth import Crypto
    assert cookie is not None
    assert "session=" in cookie
    assert str(ACCESS_TOKEN_EXPIRE_MINUTES * 60) in cookie
    cookie_values = cookie.split(";")
    session_cookie = None
    for value in cookie_values:
        if "session=" in value:
            # Get the value without 'session=' and parse it
            # The session cookie is made up of 3 values delimited by "."
            # The last two values are related to signing
            # The first value is what we stored
            session_cookie = json.loads(b64decode(value[8:].split(".")[0]))
    assert session_cookie is not None
    assert "user" in session_cookie
    user_cookie = session_cookie["user"]
    assert "exp" in user_cookie
    # The nested json should be encrypted. Trying to decode it should not work.
    with pytest.raises(json.JSONDecodeError):
        json.loads(user_cookie["session"])
    # if we decrypt it first, however, it should work
    user_session = json.loads(Crypto.decrypt(user_cookie["session"]))
    assert "id" in user_session
    assert "token" in user_session
    assert "role" in user_session
    assert "avatar_url" in user_session
    assert "name" in user_session



@pytest.mark.unit
@pytest.mark.nondestructive
def test_login_success(testclient, mock_login_success):
    response = testclient.get("/api/auth/login", allow_redirects=False)
    assert response.status_code == 307
    redirect_location = response.headers.get("location")
    assert redirect_location is not None
    response = testclient.get(redirect_location, allow_redirects=False)
    assert response.status_code == 307
    cookie = response.headers.get("set-cookie")
    check_cookie_value(cookie)
    

@pytest.mark.unit
@pytest.mark.nondestructive
def test_login_success_token(testclient, mock_login_success):
    response = testclient.get(
        "/api/auth/token-login",
        allow_redirects=False,
        headers={
            "authorization": "Bearer fake-token"})
    assert response.status_code == 200
    cookie = response.headers.get("set-cookie")
    check_cookie_value(cookie)


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "headers",
    [{},
     {"Authorization": ""},
     {"Authorization": "bad-format"}]
)
def test_login_failure_token(testclient, mock_login_success, headers):
    response = testclient.get(
        f"/api/auth/token-login",
        allow_redirects=False,
        headers=headers)
    assert response.status_code == 500


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "exc,status_code,text",
    [(AccessDeniedError, 403, "Forbidden"),
     (CustomBaseError("???"), 500, "???"),
     (Exception("???"), 500, "Could not authenticate")]
)
def test_login_exception(testclient, monkeypatch, exc,
                         status_code, text):
    def get_mock_authenticate(exc):
        async def mock_authenticate(*_):
            raise exc
        return mock_authenticate
    monkeypatch.setattr("app.api.endpoints.auth.authenticate_user",
                        get_mock_authenticate(exc))

    response = testclient.get("/api/auth/callback", allow_redirects=False)
    assert response.status_code == status_code
    assert response.json()["detail"] == text


@pytest.mark.unit
@pytest.mark.nondestructive
def test_login_no_team(monkeypatch, testclient, mock_login_success):
    async def return_no_teams(*_args, **_kwargs):
        return []
    monkeypatch.setattr("app.github.api.get_user_teams", return_no_teams)

    response = testclient.get("/api/auth/callback", allow_redirects=False)
    # Temporarily allow people who are not on an openstax team
    assert response.status_code == 307
    # Do not allow people who are not on an openstax team
    # assert response.status_code == 403


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize("endpoint", [
    "/api/jobs/"
])
def test_require_auth(testclient, endpoint):
    response = testclient.get(endpoint, allow_redirects=False)
    assert response.status_code == 401
