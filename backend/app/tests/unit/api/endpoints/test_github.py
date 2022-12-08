import pytest

from app.data_models.models import RepositorySummary


@pytest.mark.unit
@pytest.mark.nondestructive
def test_repositories(monkeypatch, testclient_with_session,
                      mock_user_service, fake_data):
    monkeypatch.setattr("app.api.endpoints.github.user_service",
                        mock_user_service)
    # GIVEN: testclient_with_session - an authenticated client
    # WHEN: the user requests a repository summary
    response = testclient_with_session.get("/api/github/repository-summary")
    # THEN:
    # the response code is 200
    assert response.status_code == 200
    payload = response.json()
    # exactly one of our fake repo is returned
    assert len(payload) == 1
    # and that fake repo has been converted into the correct model containing
    # the correct information
    first = payload[0]
    assert first == RepositorySummary.from_orm(fake_data.FAKE_REPO)
