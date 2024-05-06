# ruff: noqa: E501

import os
import re

import pytest

# Import fixtures
pytest_plugins = "tests.ui.fixtures.ui"


def get_custom_markers():
    """Function used to register custom markers.

    Define custom markers within this function to register them in pytest
    """
    return (
        "integration: mark tests that are integration tests",
        "smoke: mark tests used for smoke testing",
        "testrail: mark tests used for testrail runs",
        "ui: mark tests used for ui tests",
        "unit: mark tests as a unit test",
        "nondestructive: tests using this decorator will run in sensitive environments",
        "sensitive: the url for environments where destructive tests should not be executed",
    )


# Due to no longer using pytest-selenium because it is unmaintained (and we moved to playwright)
# we migrated the nondestructive and sensitive url config options.
# https://github.com/pytest-dev/pytest-selenium/blob/c0c1e54c68e02727a3d0b2755cc90cd162af99af/mozwebqa/mozwebqa.py
def pytest_addoption(parser):
    group = parser.getgroup("safety", "safety")
    group.addoption(
        "--destructive",
        action="store_true",
        dest="run_destructive",
        default=False,
        help="include destructive tests (tests not explicitly marked as 'nondestructive'). (disabled by default).",
    )
    parser.addoption("--github-token", default=os.getenv("GITHUB_TOKEN", None))
    group.addoption(
        "--sensitiveurl",
        action="store",
        dest="sensitive_url",
        default=r"corgi\.ce\.openstax\.org",
        metavar="str",
        help="regular expression for identifying sensitive urls.",
    )


def pytest_configure(config):
    for marker in get_custom_markers():
        config.addinivalue_line("markers", marker)

    if not config.option.run_destructive and config.option.markexpr:
        config.option.markexpr = f"nondestructive and {config.option.markexpr}"


def pytest_runtest_setup(item):
    sensitive = re.search(
        item.config.option.sensitive_url, item.config.option.base_url
    )
    destructive = "nondestructive" not in item.keywords

    if sensitive and destructive:
        # Skip the test with an appropriate message
        pytest.skip(
            "This test is destructive and the target URL is"
            "considered a sensitive environment. If this test"
            "is not destructive add the 'nondestructive' marker."
        )


@pytest.fixture(scope="session")
def api_url(base_url):
    return f"{base_url}/api"


@pytest.fixture(scope="session")
def github_token(request):
    """Return the revision"""
    config = request.config
    github_token = config.getoption("--github-token")
    assert isinstance(github_token, str) and len(github_token) > 0, (
        "Use option --github-token or env var GITHUB_TOKEN to set the"
        "token to use"
    )
    return github_token
