import pytest
from app.main import server
from fastapi.responses import RedirectResponse
from starlette.testclient import TestClient


@pytest.fixture
def fake_data():
    from datetime import datetime, timezone
    from typing import cast

    from app.data_models.models import UserSession, Role
    from app.db.schema import (Book, BookJob, Commit, Jobs, JobTypes,
                               Repository, Status, User)

    now = datetime.now(timezone.utc)

    class FakeData:
        AUDIT_DATA = {"created_at": now, "updated_at": now}
        FAKE_REPO = Repository(name="osbooks-fake-book", owner="openstax", id=1)
        FAKE_COMMIT = Commit(
            id=1,
            repository_id=FAKE_REPO.id)
        FAKE_BOOK = Book(
            commit_id=FAKE_COMMIT.id,
            slug="test",
            uuid="ooooooo",
            edition=0,
            style="test")
        FAKE_USER = User(id=1, name="Test", avatar_url="/")
        FAKE_SESSION = UserSession(
            id=cast(int, FAKE_USER.id),
            name=cast(str, FAKE_USER.name),
            avatar_url=cast(str, FAKE_USER.avatar_url),
            token="test",
            role=Role.ADMIN)
        FAKE_JOB = Jobs(
            id=1,
            user_id=FAKE_USER.id,
            status_id=1,
            job_type_id=3,
            worker_version="",
            error_message="",
            **AUDIT_DATA)
        FAKE_STATUS = Status(
            id=1,
            name="queued",
            **AUDIT_DATA)
        FAKE_JOB_TYPE = JobTypes(
            id=3,
            name="Test",
            display_name="Test job type",
            **AUDIT_DATA)
        FAKE_BOOK_JOB = BookJob(book_id=FAKE_BOOK.id, job_id=FAKE_JOB.id)
        FAKE_BOOK_JOB.book = FAKE_BOOK
        FAKE_COMMIT.books = [FAKE_BOOK]
        FAKE_REPO.commits = [FAKE_COMMIT]
        FAKE_JOB.books = [FAKE_BOOK_JOB]
        FAKE_JOB.status = FAKE_STATUS
        FAKE_JOB.user = FAKE_USER
        FAKE_JOB.job_type = FAKE_JOB_TYPE
    return FakeData


@pytest.fixture
def mock_user_service(fake_data):

    class MockUserService:
        def upsert_user_repositories(self, db, user, repositories):
            pass

        def upsert_user(self, db, user):
            pass

        def get_user_repositories(self, db, user):
            return [fake_data.FAKE_REPO]
    return MockUserService()


@pytest.fixture
def mock_jobs_service(fake_data):
    from app.db.schema import Jobs
    class MockJobsService:
        schema_model = Jobs

        async def create(self, client, db, job_in, user):
            return fake_data.FAKE_JOB

        def update(self, db, job, job_in):
            return fake_data.FAKE_JOB

        def get_jobs_in_date_range(self, db, start, end, order_by=None):
            return [fake_data.FAKE_JOB]

        def get_items_order_by(self, *_args, **_kwargs):
            return [fake_data.FAKE_JOB]

        def get(self, db, id):
            return fake_data.FAKE_JOB
    return MockJobsService()


@pytest.fixture
def mock_oauth_redirect(monkeypatch):
    class MockOAuth:
        async def authorize_redirect(self, request, redirect_uri):
            return RedirectResponse(redirect_uri)

    monkeypatch.setattr("app.api.endpoints.auth.github_oauth", MockOAuth())


@pytest.fixture
def mock_login_success(monkeypatch, mock_oauth_redirect, fake_data):
    async def mock_authenticate(*_):
        return fake_data.FAKE_SESSION

    monkeypatch.setattr("app.api.endpoints.auth.authenticate_user",
                        mock_authenticate)


@pytest.fixture
def session_cookie(testclient, mock_login_success):
    response = testclient.get(f"/api/auth/login", allow_redirects=False)
    redirect_location = response.headers.get("location")
    response = testclient.get(redirect_location, allow_redirects=False)
    return response.headers.get("set-cookie")


@pytest.fixture(scope="session")
def testclient():
    client = TestClient(server)
    yield client


@pytest.fixture
def testclient_with_session(testclient, session_cookie):
    testclient.headers = {"cookie": session_cookie}
    return testclient
