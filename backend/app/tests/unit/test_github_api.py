import json
from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import sha256
from typing import cast

import httpx
import pytest
from httpx import AsyncClient

from app.core.errors import CustomBaseError
from app.github.api import make_repo_public, push_to_github
from app.github.client import AuthenticatedClient
from app.github.models import GitHubRepo
from tests.unit.conftest import MockAsyncClient


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_get_user_and_teams(monkeypatch, mock_github_api):
    from app.data_models.models import UserSession

    exc = None
    user = None
    teams = None
    try:
        async with AsyncClient() as client:
            user = await mock_github_api.get_user(client, "")
            teams = await mock_github_api.get_user_teams(client, user.name)
    except Exception as e:
        exc = e
    assert exc is None
    assert isinstance(user, UserSession)
    assert isinstance(teams, list)
    assert len(teams) > 0


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_get_book_repository(monkeypatch, mock_github_api):
    exc = None
    repo = None
    books = None
    timestamp = None
    commit_sha = None
    try:
        async with AsyncClient() as client:
            (
                repo,
                commit_sha,
                timestamp,
                books,
            ) = await mock_github_api.get_book_repository(
                client, "tiny-book", "openstax", "main"
            )
    except Exception as e:
        exc = e
    assert exc is None
    assert repo
    assert repo.name == "tiny-book"
    assert isinstance(commit_sha, str)
    assert isinstance(timestamp, datetime)
    assert isinstance(books, list)
    assert isinstance(repo, GitHubRepo)
    assert isinstance(repo.visibility, str)
    assert datetime.fromisoformat(
        "2024-06-14T16:26:24.611Z"
    ) == datetime.fromisoformat("2024-06-14T16:26:24.611+00:00")
    assert len(books) > 0


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_get_book_collections(monkeypatch, mock_github_api):
    exc = None
    collections = None
    try:
        async with AsyncClient() as client:
            collections = await mock_github_api.get_collections(
                client, "tiny-book", "openstax", "main"
            )
    except Exception as e:
        exc = e
    assert exc is None
    assert isinstance(collections, dict)
    assert "book-slug1.collection.xml" in collections
    assert collections["book-slug1.collection.xml"] is not None
    assert len(collections["book-slug1.collection.xml"]) > 0


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_get_user_repositories(monkeypatch, mock_github_api):
    from app.github import GitHubRepo

    exc = None
    repos = None
    try:
        async with AsyncClient() as client:
            repos = await mock_github_api.get_user_repositories(
                client, "org:openstax osbooks in:name is:public"
            )
    except Exception as e:
        exc = e
    assert exc is None
    assert isinstance(repos, list)
    assert len(repos) > 0
    assert isinstance(repos[0], GitHubRepo)


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_push_to_github(mock_http_client):
    owner = "test_owner"
    repo = "test_repo"
    path = "README.md"
    content = original_content = "# README"
    branch = "main"
    sha = sha256(content.encode()).hexdigest()
    commit_message = "commit message"
    client: MockAsyncClient = mock_http_client(
        get={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}?ref={branch}": {
                "content": b64encode(content.encode()).decode(),
                "sha": sha,
            }
        },
        put={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}": "OK"
        },
    )

    # GIVEN: No changes to existing file
    # WHEN: A push is attempted
    with pytest.raises(CustomBaseError) as hse:
        await push_to_github(
            cast(AuthenticatedClient, client),
            path,
            content,
            owner,
            repo,
            branch,
            commit_message,
            True,
        )

    # THEN: An error is raised before a PUT request is made
    assert len(client.responses) == 1
    request: httpx.Request = client.responses[-1].request
    assert request.method == "GET"
    assert hse.match("No changes to push")

    # GIVEN: Changes to existing file
    content = f"{original_content} with changes"
    new_content = b64encode(content.encode()).decode()
    client.reset_history()

    # WHEN: A push is attempted
    await push_to_github(
        cast(AuthenticatedClient, client),
        path,
        content,
        owner,
        repo,
        branch,
        commit_message,
        True,
    )

    # THEN: There is a GET and PUT request; the PUT request has correct data
    assert len(client.responses) == 2
    assert [r.request.method for r in client.responses] == ["GET", "PUT"]
    put_request: httpx.Request = client.responses[1].request
    response_content = put_request.content
    data = json.loads(response_content)
    # Sends to new content
    assert data.get("content") == new_content
    # Sends the sha of file being updated
    assert data.get("sha") == sha
    assert data.get("branch") == branch
    assert data.get("message") == commit_message

    client.reset_history()

    # GIVEN: Changes to non-existing file
    content = f"{original_content} with changes"
    # WHEN: A push is attempted
    await push_to_github(
        cast(AuthenticatedClient, client),
        path,
        content,
        owner,
        repo,
        branch,
        commit_message,
        False,
    )

    # THEN: There is one PUT request; the PUT request has correct data
    assert len(client.responses) == 1
    assert client.responses[0].request.method == "PUT"
    put_request: httpx.Request = client.responses[0].request
    response_content = put_request.content
    data = json.loads(response_content)
    # Sends to new content
    assert data.get("content") == new_content
    # No sha because file is new
    assert data.get("sha") is None
    assert data.get("branch") == branch
    assert data.get("message") == commit_message

    client.reset_history()
    # WHEN: Changes are pushed with a sha
    await push_to_github(
        cast(AuthenticatedClient, client),
        path,
        content,
        owner,
        repo,
        branch,
        commit_message,
        False,
        sha,
    )
    # THEN: Only one request is made
    assert [r.request.method for r in client.responses] == ["PUT"]

    # GIVEN: Changes to non-existing file; an error from github
    client: MockAsyncClient = mock_http_client(
        get={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}?ref={branch}": httpx.Response(404)
        },
        put={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}": httpx.Response(404)
        },
    )
    content = f"{original_content} with changes"
    # WHEN: Changes are pushed
    with pytest.raises(httpx.HTTPStatusError) as hse:
        await push_to_github(
            cast(AuthenticatedClient, client),
            path,
            content,
            owner,
            repo,
            branch,
            commit_message,
            False,
        )

    # THEN: An error is raised when a PUT request is made
    assert len(client.responses) == 1
    request: httpx.Request = client.responses[-1].request
    assert request.method == "PUT"
    assert hse.match("404")

    client.reset_history()
    # GIVEN: Changes to existing file; error from github
    with pytest.raises(httpx.HTTPStatusError) as hse:
        await push_to_github(
            cast(AuthenticatedClient, client),
            path,
            content,
            owner,
            repo,
            branch,
            commit_message,
            True,
        )

    # THEN: An error is raised when a GET request is made
    assert len(client.responses) == 1
    request: httpx.Request = client.responses[-1].request
    assert request.method == "GET"
    assert hse.match("404")


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.asyncio
async def test_make_repo_public(mock_http_client):
    owner = "test_owner"
    repo = "test_repo"
    path = ".github/settings.yml"
    text = b64encode(b"{}").decode()
    sha = sha256(b"{}").hexdigest()
    content = {"content": text, "sha": sha}
    branch = "main"
    # GIVEN: A repository with a settings yaml file
    client: MockAsyncClient = mock_http_client(
        get={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}?ref={branch}": content
        },
        put={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}": "OK"
        },
    )

    # WHEN: We attempt to make it public
    await make_repo_public(client, owner, repo)
    # THEN: There are 2 requests and the expected data is sent
    assert [r.request.method for r in client.responses] == ["GET", "PUT"]
    put_request = client.responses[-1].request
    data = json.loads(put_request.content)
    assert (
        b64decode(data.get("content", "")) == b"repository:\n  private: false\n"
    )
    assert data.get("sha") == sha
    assert data.get("branch") == branch

    # GIVEN: Private is set to true
    client: MockAsyncClient = mock_http_client(
        get={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}?ref={branch}": content
            | {"content": b64encode(b"repository:\n  private: true\n").decode()}
        },
        put={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}": "OK"
        },
    )
    # WHEN: We attempt to make it public
    await make_repo_public(client, owner, repo)
    # THEN: It works as if private was not set
    assert [r.request.method for r in client.responses] == ["GET", "PUT"]
    put_request = client.responses[-1].request
    data = json.loads(put_request.content)
    assert (
        b64decode(data.get("content", "")) == b"repository:\n  private: false\n"
    )

    # GIVEN: Missing settings file
    client: MockAsyncClient = mock_http_client(
        get={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}?ref={branch}": httpx.Response(404)
        },
        put={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}": httpx.Response(
                500, text="This should not happen"
            )
        },
    )
    # WHEN: We attempt to make it public
    # THEN: An error about missing settings file is raised
    with pytest.raises(CustomBaseError) as cbe:
        await make_repo_public(client, owner, repo)
    assert cbe.match("Could not get settings file")

    # GIVEN: settings file that is already public
    client: MockAsyncClient = mock_http_client(
        get={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}?ref={branch}": (
                content
                | {
                    "content": b64encode(
                        b"repository:\n  private: false\n"
                    ).decode()
                }
            )
        },
        put={
            "https://api.github.com/repos/"
            f"{owner}/{repo}/contents/{path}": httpx.Response(
                500, text="This should not happen"
            )
        },
    )
    # WHEN: We attempt to make it public
    # THEN: An error about repo already being public or a possible error in
    # settings.yml is raised
    with pytest.raises(CustomBaseError) as cbe:
        await make_repo_public(client, owner, repo)
    assert cbe.match("repository may already be public")
    assert cbe.match("settings.yml")
