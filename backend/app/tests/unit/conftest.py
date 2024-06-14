import os
from typing import Any

import httpx
import pytest
from fastapi.responses import RedirectResponse
from starlette.testclient import TestClient


def pytest_addoption(parser):
    parser.addoption("--init-test-data", action="store_true")


def pytest_configure(config):
    os.environ.setdefault(
        "SESSION_SECRET", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    )
    init_test_data = config.getoption("--init-test-data")
    if init_test_data:
        token = config.getoption("--github-token")
        if token is not None:
            from tests.unit.init_test_data import main

            main(token)
        else:
            raise Exception(
                "--github-token is required when initializing " "test data"
            )


@pytest.fixture
def mock_github_api():
    """Uses vcr to fake responses from GitHub API"""
    from tests.unit.init_test_data import (
        mock_get_book_repository,
        mock_get_collections,
        mock_get_user,
        mock_get_user_repositories,
        mock_get_user_teams,
    )

    # Namespace functions in a class purely for ease of use
    class MockGitHubAPI:
        get_user = mock_get_user
        get_user_teams = mock_get_user_teams
        get_collections = mock_get_collections
        get_user_repositories = mock_get_user_repositories
        get_book_repository = mock_get_book_repository

    return MockGitHubAPI


@pytest.fixture
def fake_data():
    """Mock database data"""
    from datetime import datetime, timezone
    from typing import cast

    from app.data_models.models import Role, UserSession
    from app.db.schema import (
        Book,
        BookJob,
        Commit,
        Jobs,
        JobTypes,
        Repository,
        Status,
        User,
    )

    now = datetime.now(timezone.utc)

    class FakeData:
        AUDIT_DATA = {"created_at": now, "updated_at": now}
        FAKE_REPO = Repository(name="osbooks-fake-book", owner="openstax", id=1)
        FAKE_COMMIT = Commit(
            id=1,
            repository_id=FAKE_REPO.id,
            timestamp=datetime.fromisoformat("2024-06-05T17:30:24.311Z"),
        )
        FAKE_COMMIT2 = Commit(
            id=2,
            repository_id=FAKE_REPO.id,
            timestamp=datetime.fromisoformat("2024-06-05T17:30:53.909Z"),
        )
        FAKE_BOOK = Book(
            commit_id=FAKE_COMMIT.id,
            slug="test",
            uuid="ooooooo",
            edition=0,
            style="test",
        )
        FAKE_BOOK2 = Book(
            commit_id=FAKE_COMMIT2.id,
            slug="test-2",
            uuid="ooooooo",
            edition=0,
            style="test",
        )
        FAKE_USER = User(id=1, name="Test", avatar_url="/")
        FAKE_SESSION = UserSession(
            id=cast(int, FAKE_USER.id),
            name=cast(str, FAKE_USER.name),
            avatar_url=cast(str, FAKE_USER.avatar_url),
            token="test",
            role=Role.ADMIN,
        )
        FAKE_JOB = Jobs(
            id=1,
            user_id=FAKE_USER.id,
            status_id=1,
            job_type_id=3,
            worker_version="",
            error_message="",
            **AUDIT_DATA,
        )
        FAKE_STATUS = Status(id=1, name="queued", **AUDIT_DATA)
        FAKE_JOB_TYPE = JobTypes(
            id=3, name="Test", display_name="Test job type", **AUDIT_DATA
        )
        FAKE_BOOK_JOB = BookJob(book_id=FAKE_BOOK.id, job_id=FAKE_JOB.id)
        FAKE_BOOK_JOB.book = FAKE_BOOK
        FAKE_COMMIT.books = [FAKE_BOOK]
        FAKE_COMMIT2.books = [FAKE_BOOK2]
        FAKE_REPO.commits = [FAKE_COMMIT, FAKE_COMMIT2]
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
            from app.data_models.models import Job

            job_model = Job.from_orm(job).dict(exclude_unset=True)
            job_in_dict = job_in.dict(exclude_unset=True)
            for k in job_in_dict:
                if job_in_dict[k] is None:
                    del job_in_dict[k]
            job_model.update(job_in_dict)

            return job_model

        def get_jobs_in_date_range(self, db, start, end, order_by=None):
            return [fake_data.FAKE_JOB]

        def get_items_order_by(self, *_args, **_kwargs):
            return [fake_data.FAKE_JOB]

        def get_items_by(self, *_args, **_kwargs):
            return [fake_data.FAKE_JOB]

        def get(self, *_args, **_kwargs):
            return fake_data.FAKE_JOB

    return MockJobsService()


@pytest.fixture
def mock_oauth_redirect(monkeypatch, fake_data):
    class MockOAuth:
        async def authorize_redirect(self, request, redirect_uri):
            return RedirectResponse(redirect_uri)

        async def authorize_access_token(self, *_):
            return {"access_token": fake_data.FAKE_SESSION.token}

    monkeypatch.setattr("app.api.endpoints.auth.github_oauth", MockOAuth())


@pytest.fixture
def mock_login_success(
    monkeypatch, mock_user_service, mock_oauth_redirect, mock_github_api
):
    async def nop(*_args, **_kwargs):
        pass

    monkeypatch.setattr(
        "app.api.endpoints.auth.get_user", mock_github_api.get_user
    )
    monkeypatch.setattr(
        "app.github.api.get_user_teams", mock_github_api.get_user_teams
    )
    monkeypatch.setattr(
        "app.api.endpoints.auth.user_service", mock_user_service
    )
    monkeypatch.setattr("app.api.endpoints.auth.sync_user_repositories", nop)


@pytest.fixture
def mock_session():
    def inner(result_getter=lambda *_: []):
        class MockSession:
            def __init__(self):
                self.calls = []
                self.added_items = []
                self.did_rollback = False
                self.did_commit = False
                self.flush_count = 0

            def execute(self, query):
                self.calls.append(query)

            def scalars(self, query):
                self.calls.append(query)
                return MockResult()

            def add(self, item):
                self.added_items.append(item)
                self.calls.append(f"INSERT INTO {item.__class__.__name__} ...")

            def merge(self, item):
                self.added_items.append(item)
                self.calls.append(
                    f"INSERT OR UPDATE INTO {item.__class__.__name__} ..."
                )

            def flush(self):
                self.flush_count += 1

            def rollback(self):
                self.did_rollback = True

            def commit(self):
                self.did_commit = True

            @property
            def calls_str(self):
                return "\n\n".join(str(c) for c in self.calls)

        mock_session = MockSession()

        class MockResult:
            def all(self):
                return result_getter(mock_session)

            def first(self):
                results = self.all()
                return (
                    None if results is None or len(results) == 0 else results[0]
                )

        return mock_session

    return inner


class MockAsyncClient(httpx.AsyncClient):
    responses: list[httpx.Response]

    def reset_history(self):
        while self.responses:
            self.responses.pop()


@pytest.fixture
def mock_http_client():
    def inner(
        **responses_by_method: dict[httpx.URL, httpx.Response | str | dict],
    ) -> MockAsyncClient:
        responses: list[httpx.Response] = []
        responses_by_method = {
            k.lower(): v for k, v in responses_by_method.items()
        }

        def handler(request: httpx.Request):
            url = request.url
            method = request.method
            if isinstance(method, bytearray):
                method = method.decode()
            planned_response = responses_by_method.get(method.lower(), {}).get(
                url
            )
            if planned_response is None:
                response = httpx.Response(404, request=request)
            elif isinstance(planned_response, httpx.Response):
                response = planned_response
            else:
                response = httpx.Response(
                    200, json=planned_response, request=request
                )
            responses.append(response)
            return response

        client = MockAsyncClient(
            mounts={"all://": httpx.MockTransport(handler)}
        )
        client.responses = responses
        return client

    return inner


@pytest.fixture
def session_cookie(testclient, mock_login_success):
    response = testclient.get("/api/auth/login", allow_redirects=False)
    redirect_location = response.headers.get("location")
    response = testclient.get(redirect_location, allow_redirects=False)
    return response.headers.get("set-cookie")


@pytest.fixture
def testclient():
    from app.main import server

    client = TestClient(server)
    yield client


@pytest.fixture
def testclient_with_session(testclient, session_cookie):
    testclient.headers = {"cookie": session_cookie}
    return testclient
