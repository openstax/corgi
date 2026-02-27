import pytest
from httpx import AsyncClient

from app.github.api import get_tags

OWNER = "openstax"
REPO = "enki"
BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/tags"


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
    from datetime import datetime

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


def gh_url(page=1, per_page=5):
    return f"{BASE_URL}?per_page={per_page}&page={page}"


def make_tags(names):
    return [{"name": n} for n in names]


@pytest.mark.asyncio
async def test_get_tags_filters_by_pattern(mock_http_client):
    # GIVEN: GitHub returns matching and non-matching tags
    mock_client = mock_http_client(
        get={
            gh_url(per_page=5): make_tags(
                ["20260225.221405", "not-a-version", "20260224.100000"]
            )
        }
    )

    # WHEN: get_tags is called with the version pattern
    result = await get_tags(mock_client, OWNER, REPO, 5, r"^\d+\.\d+$")

    # THEN: Only pattern-matching tags are returned
    assert result == ["20260225.221405", "20260224.100000"]


@pytest.mark.asyncio
async def test_get_tags_no_pattern(mock_http_client):
    # GIVEN: GitHub returns several tags
    mock_client = mock_http_client(
        get={
            gh_url(per_page=5): make_tags(
                ["v1.0", "not-a-version", "20260224.100000"]
            )
        }
    )

    # WHEN: get_tags is called without a pattern
    result = await get_tags(mock_client, OWNER, REPO, 5, None)

    # THEN: All tags are returned
    assert result == ["v1.0", "not-a-version", "20260224.100000"]


@pytest.mark.asyncio
async def test_get_tags_respects_count(mock_http_client):
    # GIVEN: GitHub returns more tags than requested
    mock_client = mock_http_client(
        get={
            gh_url(per_page=3): make_tags(
                [
                    "20260225.221405",
                    "20260224.100000",
                    "20260223.100000",
                    "20260222.100000",
                ]
            )
        }
    )

    # WHEN: only 3 tags are requested
    result = await get_tags(mock_client, OWNER, REPO, 3, r"^\d+\.\d+$")

    # THEN: Only 3 are returned
    assert result == ["20260225.221405", "20260224.100000", "20260223.100000"]


@pytest.mark.asyncio
async def test_get_tags_paginates(mock_http_client):
    # GIVEN: Page 1 is full but contains a non-matching tag, so page 2 is needed
    # to satisfy the requested count. per_page = min(count=3, 100) = 3.
    page1 = make_tags(["20260002.000000", "not-a-version", "20260001.000000"])
    page2 = make_tags(["20260000.000000"])
    mock_client = mock_http_client(
        get={
            gh_url(page=1, per_page=3): page1,
            gh_url(page=2, per_page=3): page2,
        }
    )

    # WHEN: 3 matching tags are requested (page 1 only yields 2 matches)
    result = await get_tags(mock_client, OWNER, REPO, 3, r"^\d+\.\d+$")

    # THEN: Tags from both pages are returned
    assert len(result) == 3
    assert result[-1] == "20260000.000000"


@pytest.mark.asyncio
async def test_get_tags_empty_response(mock_http_client):
    # GIVEN: GitHub returns no tags
    mock_client = mock_http_client(get={gh_url(per_page=5): []})

    # WHEN: get_tags is called
    result = await get_tags(mock_client, OWNER, REPO, 5, r"^\d+\.\d+$")

    # THEN: Empty list is returned
    assert result == []
