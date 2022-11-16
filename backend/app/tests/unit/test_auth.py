from datetime import datetime, timedelta, timezone
from typing import Any, cast

import app.api.endpoints.auth
import app.github.api
import app.github.client
import app.github.utils
import pytest
from app.api.endpoints.auth import callback
from app.core.auth import active_user, get_user_role
from app.data_models.models import Role, UserSession
from fastapi import HTTPException


class MockRequest:
    def __init__(self, error_type):
        user = UserSession(
            id=456, token="abc", role=Role.ADMIN, avatar_url="something",
            name="Test"
        )
        self.mock_user_cookie = {
            "exp": (datetime.now(timezone.utc)
                    + timedelta(minutes=5)).timestamp(),
            "session": user.json()
        }
        if error_type == "expired":
            self.mock_user_cookie["exp"] = 0
        elif error_type == "not_authenticated":
            self.mock_user_cookie = None
        self.session = {}
        self.session["user"] = self.mock_user_cookie


class MockResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {}

    @property
    def text(self):
        return ""


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    'teams,role',
    [
        ([], None),
        (['ce-tech'], Role.ADMIN),
        (['some-other-team', Role.DEFAULT])
    ]
)
def test_get_user_role(teams, role):
    assert get_user_role(teams) == role


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    'req,status_code',
    [
        (MockRequest("expired"), 401),
        (MockRequest("not_authenticated"), 401),
    ]
)
def test_active_user_dependency_fails(
    req: MockRequest,
    status_code: int
):
    with pytest.raises(HTTPException) as http_exc:
        active_user(cast(Any, req))
    assert http_exc.value.status_code == status_code


@pytest.mark.unit
@pytest.mark.nondestructive
def test_active_user_dependency_succeeds():
    http_exc = None
    try:
        _ = active_user(cast(Any, MockRequest("")))
    except HTTPException as e:
        http_exc = e
    assert http_exc is None


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_auth_callback_fails_correctly(monkeypatch):
    request = MockRequest("")

    async def mock_post(*args, **kwargs):
        class MockAccessResponse(MockResponse):
            @property
            def text(self):
                return ""
        return MockAccessResponse()
    monkeypatch.setattr(app.github.client.AsyncClient, "post", mock_post)
    with pytest.raises(HTTPException) as http_exc:
        await callback(cast(Any, request))
        assert http_exc.value.status_code == 500


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_auth_callback_fails_when_not_on_team(monkeypatch):
    request = MockRequest("")

    async def mock_post(*args, **kwargs):
        class MockAccessResponse(MockResponse):
            @property
            def text(self):
                return "access_token=1234"
        return MockAccessResponse()

    async def mock_get(self, url, **kwargs):
        if url == "https://api.github.com/user":
            class MockUserResponse(MockResponse):
                def json(self):
                    return {
                        "login": "FAKE_USER",
                        "avatar_url": "FAKE_AVATAR_URL",
                        "id": "FAKE_ID"
                    }
            return MockUserResponse()
        return MockResponse()

    async def get_empty_teams(*args):
        return []
    monkeypatch.setattr(app.github.client.AsyncClient, "post", mock_post)
    monkeypatch.setattr(app.github.client.AsyncClient, "get", mock_get)
    monkeypatch.setattr(app.github.api, "get_user_teams", get_empty_teams)
    with pytest.raises(HTTPException) as http_exc:
        await callback(cast(Any, request))
        assert http_exc.value.status_code == 403


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_auth_callback(monkeypatch):
    request = MockRequest("")

    async def mock_post(*args, **kwargs):
        class MockAccessResponse(MockResponse):
            @property
            def text(self):
                return "access_token=1234"
        return MockAccessResponse()

    async def mock_get(self, url, **kwargs):
        if url == "https://api.github.com/user":
            class MockUserResponse(MockResponse):
                def json(self):
                    return {
                        "login": "FAKE_USER",
                        "avatar_url": "FAKE_AVATAR_URL",
                        "id": 1234
                    }
            return MockUserResponse()
        return MockResponse()

    async def get_fake_teams(*args):
        return ["FAKE-TEAM"]

    async def nop(*args):
        pass
    monkeypatch.setattr(app.github.client.AsyncClient, "post", mock_post)
    monkeypatch.setattr(app.github.client.AsyncClient, "get", mock_get)
    monkeypatch.setattr(app.api.endpoints.auth, "sync_user_data", nop)
    monkeypatch.setattr(app.github.api, "get_user_teams", get_fake_teams)
    await callback(cast(Any, request))
    assert UserSession.parse_raw(
        request.session["user"]["session"]).token == "1234"
