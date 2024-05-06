import pytest

from app.github import GitHubRepo


@pytest.mark.unit
@pytest.mark.nondestructive
def test_github_repo_model():
    model = GitHubRepo.from_node(
        {"name": "test", "databaseId": 1, "viewerPermission": "WRITE"}
    )
    assert model.name == "test"
    assert model.database_id == "1"
    assert model.viewer_permission == "WRITE"
