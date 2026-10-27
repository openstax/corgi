import pytest
from pydantic import ValidationError

from app.data_models.models import ArtifactBase, JobUpdate


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/artifacts/build-1.zip",
        "http://example.com:8080/artifacts/build-1.zip",
        "HTTPS://example.com/artifacts/build-1.zip",
    ],
)
def test_artifact_base_accepts_http_urls(url):
    artifact = ArtifactBase(slug="book", url=url)

    assert artifact.url == url


@pytest.mark.parametrize("url", [None, ""])
def test_artifact_base_allows_missing_url(url):
    artifact = ArtifactBase(slug="book", url=url)

    assert artifact.url == url


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "ftp://example.com/artifacts/build-1.zip",
        "//example.com/artifacts/build-1.zip",
        "/artifacts/build-1.zip",
        "https:///artifacts/build-1.zip",
        "https://user:password@example.com/artifacts/build-1.zip",
        "https://example.com:invalid/artifacts/build-1.zip",
        " https://example.com/artifacts/build-1.zip",
        "https://example.com/artifacts/build-1.zip\n",
    ],
)
def test_artifact_base_rejects_unsafe_or_malformed_urls(url):
    with pytest.raises(ValidationError):
        ArtifactBase(slug="book", url=url)


def test_job_update_validates_legacy_artifact_url_string():
    update = JobUpdate(
        status_id="completed",
        artifact_urls="https://example.com/artifacts/build-1.zip",
    )

    assert update.artifact_urls == "https://example.com/artifacts/build-1.zip"


def test_job_update_rejects_unsafe_legacy_artifact_url_string():
    with pytest.raises(ValidationError):
        JobUpdate(status_id="completed", artifact_urls="javascript:alert(1)")


def test_job_update_validates_artifact_url_list():
    update = JobUpdate(
        status_id="completed",
        artifact_urls=[
            {"slug": "book", "url": "https://example.com/artifacts/build-1.zip"}
        ],
    )

    assert (
        update.artifact_urls[0].url
        == "https://example.com/artifacts/build-1.zip"
    )


def test_job_update_rejects_unsafe_artifact_url_in_list():
    with pytest.raises(ValidationError):
        JobUpdate(
            status_id="completed",
            artifact_urls=[{"slug": "book", "url": "javascript:alert(1)"}],
        )
