import pytest


@pytest.mark.unit
@pytest.mark.nondestructive
def test_get_tags_returns_intersection(monkeypatch, testclient_with_session):
    # GIVEN: The combined fetch returns tags present in both sources
    async def mock_get_tags(owner, repo, pattern, count):
        return ["20260225.221405", "20260224.100000"]

    monkeypatch.setattr("app.api.endpoints.version._get_tags", mock_get_tags)

    # WHEN: the tags endpoint is called
    response = testclient_with_session.get(
        "/api/version/tags/openstax::enki", params={"count": 5}
    )

    # THEN: the intersection is returned
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == ["20260225.221405", "20260224.100000"]
    assert payload["count"] == 2


@pytest.mark.unit
@pytest.mark.nondestructive
def test_get_tags_empty_intersection(monkeypatch, testclient_with_session):
    # GIVEN: No tags exist in both sources
    async def mock_get_tags(owner, repo, pattern, count):
        return []

    monkeypatch.setattr("app.api.endpoints.version._get_tags", mock_get_tags)

    # WHEN: the tags endpoint is called
    response = testclient_with_session.get("/api/version/tags/openstax::enki")

    # THEN: an empty list is returned with count 0
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == []
    assert payload["count"] == 0


@pytest.mark.unit
@pytest.mark.nondestructive
def test_get_tags_count_capped_at_25(monkeypatch, testclient_with_session):
    # GIVEN: the caller requests more than the max
    received_count = {}

    async def mock_get_tags(owner, repo, pattern, count):
        received_count["value"] = count
        return []

    monkeypatch.setattr("app.api.endpoints.version._get_tags", mock_get_tags)

    # WHEN: count=100 is requested
    testclient_with_session.get(
        "/api/version/tags/openstax::enki", params={"count": 100}
    )

    # THEN: the inner fetch is called with at most 25
    assert received_count["value"] <= 25


@pytest.mark.unit
@pytest.mark.nondestructive
def test_get_tags_requires_auth(testclient):
    # GIVEN: an unauthenticated client
    # WHEN: the tags endpoint is called without a session
    response = testclient.get("/api/version/tags/openstax::enki")

    # THEN: access is denied
    assert response.status_code in (401, 403)
