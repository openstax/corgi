
import pytest
from httpx import AsyncClient


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
            repo, commit_sha, timestamp, books = \
                await mock_github_api.get_book_repository(
                    client, "tiny-book", "openstax", "main")
    except Exception as e:
        exc = e
    assert exc is None
    assert repo
    assert repo.name == "tiny-book"
    assert isinstance(commit_sha, str)
    assert isinstance(timestamp, datetime)
    assert isinstance(books, list)
    assert len(books) > 0


@pytest.mark.asyncio
async def test_get_book_collections(monkeypatch, mock_github_api):
    from lxml import etree
    exc = None
    collections = None
    try:
        async with AsyncClient() as client:
            collections = await mock_github_api.get_collections(
                client, "tiny-book", "openstax", "main")
    except Exception as e:
        exc = e
    assert exc is None
    assert isinstance(collections, dict)
    assert "book-slug1.collection.xml" in collections
    assert collections["book-slug1.collection.xml"] is not None
    assert len(collections["book-slug1.collection.xml"]) > 0


@pytest.mark.asyncio
async def test_get_user_repositories(monkeypatch, mock_github_api):
    from app.github import GitHubRepo
    exc = None
    repos = None
    try:
        async with AsyncClient() as client:
            repos = await mock_github_api.get_user_repositories(
                client, "org:openstax osbooks in:name is:public")
    except Exception as e:
        exc = e
    assert exc is None
    assert isinstance(repos, list)
    assert len(repos) > 0
    assert isinstance(repos[0], GitHubRepo)
