from typing import cast, Any

import pytest
from app.data_models.models import Role, UserSession
from app.github import GitHubRepo, sync_user_data


FAKE_USER = UserSession(id=1, token="fake", role=Role.DEFAULT, avatar_url="",
                        name="TestUser")
FAKE_REPO = GitHubRepo(name="Test", database_id="1234",
                       viewer_permission="WRITE")


@pytest.fixture
def mock_get_user_repositories(monkeypatch):
    async def get_user_repositories(client, query):
        return [FAKE_REPO]
    monkeypatch.setattr("app.github.utils.get_user_repositories",
                        get_user_repositories)


@pytest.fixture
def mock_user_service(monkeypatch):
    class MockUserService:
        def upsert_user(self, _db, user: UserSession):
            assert user == FAKE_USER

    monkeypatch.setattr("app.github.utils.user_service",
                        MockUserService())


@pytest.fixture
def mock_repository_service(monkeypatch):
    class MockRepositoryService:
        def upsert_repositories(self, _db, repos):
            assert len(repos) == 1
            assert repos[0].id == FAKE_REPO.database_id
            assert repos[0].name == FAKE_REPO.name
            assert repos[0].owner == "openstax"  # default
        
        def upsert_user_repositories(self, _db, user_id, user_repos):
            assert len(user_repos) == 1
            assert user_repos[0] == FAKE_REPO
            assert user_id == FAKE_USER.id

    monkeypatch.setattr("app.github.utils.repository_service",
                        MockRepositoryService())


@pytest.mark.asyncio
async def test_sync_user_data(mock_get_user_repositories, mock_user_service,
                              mock_repository_service):
    # cast here to get the type checker to ignore
    fake_client = cast(Any, None)
    fake_db = cast(Any, None)
    exception = None
    try:
        await sync_user_data(fake_client, fake_db, FAKE_USER)
    except Exception as e:
        exception = e
    assert exception is None
