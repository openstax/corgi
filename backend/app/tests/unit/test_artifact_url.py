import pytest
from pydantic import ValidationError

from app.data_models.models import (
    ArtifactBase,
    JobUpdate,
    validate_artifact_url,
)

ARTIFACT_URL_CASES = {
    "accepted_by_both": [
        {
            "name": "HTTPS artifact URL",
            "url": "https://example.com/artifacts/build-1.zip",
        },
        {
            "name": "HTTP URL with a non-default port",
            "url": "http://example.com:8080/artifacts/build-1.zip",
        },
        {
            "name": "uppercase scheme",
            "url": "HTTPS://example.com/artifacts/build-1.zip",
        },
        {
            "name": "valid percent escape in the authority",
            "url": "https://example%2ecom/artifacts/build-1.zip",
        },
        {
            "name": "malformed percent escapes outside the authority",
            "url": "https://example.com/artifacts/%zz.zip?download=%xx",
        },
    ],
    "rejected_by_both": [
        {"name": "script URL", "url": "javascript:alert(1)"},
        {"name": "data URL", "url": "data:text/html,<script>alert(1)</script>"},
        {
            "name": "unsupported scheme",
            "url": "ftp://example.com/artifacts/build-1.zip",
        },
        {
            "name": "protocol-relative URL",
            "url": "//example.com/artifacts/build-1.zip",
        },
        {"name": "relative URL", "url": "/artifacts/build-1.zip"},
        {"name": "missing authority", "url": "https:///artifacts/build-1.zip"},
        {
            "name": "whitespace in authority",
            "url": "https://bad host.example/artifact.zip",
        },
        {
            "name": "malformed percent escape in authority",
            "url": "https://example.com%zz/artifact.zip",
        },
        {
            "name": "backslash in authority",
            "url": "https://example.com\\evil/artifact.zip",
        },
        {
            "name": "backslash instead of scheme slashes",
            "url": "https:\\example.com/artifacts/build-1.zip",
        },
        {
            "name": "empty userinfo",
            "url": "https://@example.com/artifacts/build-1.zip",
        },
        {
            "name": "credentials",
            "url": "https://user:password@example.com/artifacts/build-1.zip",
        },
        {
            "name": "non-numeric port",
            "url": "https://example.com:invalid/artifact.zip",
        },
        {
            "name": "port above the valid range",
            "url": "https://example.com:65536/artifact.zip",
        },
        {
            "name": "leading whitespace",
            "url": " https://example.com/artifacts/build-1.zip",
        },
        {
            "name": "trailing newline",
            "url": "https://example.com/artifacts/build-1.zip\n",
        },
    ],
    "known_parser_differences": [
        {
            "name": "WHATWG URL rejects an out-of-range numeric IPv4 host; urlsplit accepts it as a nonempty hostname",
            "url": "https://256.0.0.1/artifact.zip",
            "frontend_accepts": False,
            "backend_accepts": True,
        }
    ],
    "optional_value_differences": [
        {
            "name": "null is treated as missing by the backend",
            "url": None,
            "frontend_accepts": False,
            "backend_passes_through": True,
        },
        {
            "name": "empty string is treated as missing by the backend",
            "url": "",
            "frontend_accepts": False,
            "backend_passes_through": True,
        },
    ],
}


@pytest.mark.parametrize(
    "case",
    ARTIFACT_URL_CASES["accepted_by_both"],
    ids=lambda case: case["name"],
)
def test_validate_artifact_url_accepts_shared_urls(case):
    assert validate_artifact_url(case["url"]) == case["url"]


@pytest.mark.parametrize(
    "case",
    ARTIFACT_URL_CASES["rejected_by_both"],
    ids=lambda case: case["name"],
)
def test_validate_artifact_url_rejects_shared_urls(case):
    with pytest.raises(ValueError):
        validate_artifact_url(case["url"])


@pytest.mark.parametrize(
    "case",
    ARTIFACT_URL_CASES["known_parser_differences"],
    ids=lambda case: case["name"],
)
def test_validate_artifact_url_documents_parser_difference(case):
    if case["backend_accepts"]:
        assert validate_artifact_url(case["url"]) == case["url"]
    else:
        with pytest.raises(ValueError):
            validate_artifact_url(case["url"])


@pytest.mark.parametrize(
    "case",
    ARTIFACT_URL_CASES["optional_value_differences"],
    ids=lambda case: case["name"],
)
def test_validate_artifact_url_documents_optional_value_difference(case):
    if case["backend_passes_through"]:
        assert validate_artifact_url(case["url"]) == case["url"]
    else:
        with pytest.raises(ValueError):
            validate_artifact_url(case["url"])


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
        "https://bad host.example/artifact.zip",
        "https://%zz/artifact.zip",
        "https://example.com\\evil/artifact.zip",
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
