import os

import pytest
import requests


# Get values we need to setup the environment from the command line or through
# env vars
def pytest_addoption(parser):
    group = parser.getgroup("corgi", "corgi")
    group.addoption(
        "--stack-name",
        default=os.getenv("STACK_NAME", "dev"),
        help="The name of the stack, used in the version endpoint",
    )
    parser.addoption(
        "--tag",
        default=os.getenv("TAG", "dev"),
        help="The tag used on the images",
    )
    parser.addoption("--revision", default=os.getenv("REVISION", "dev"))


@pytest.fixture(scope="session")
def api_url(base_url):
    return f"{base_url}/api"


@pytest.fixture(scope="session")
def tag(request):
    """Return the tag"""
    config = request.config
    tag = config.getoption("tag")
    if tag is not None:
        return tag
    else:
        return "dev"


@pytest.fixture(scope="session")
def stack_name(request):
    """Return the name of the stack"""
    config = request.config
    stack_name = config.getoption("stack_name")
    if stack_name is not None:
        return stack_name
    else:
        return "dev"


@pytest.fixture(scope="session")
def revision(request):
    """Return the revision"""
    config = request.config
    revision = config.getoption("revision")
    if revision is not None:
        return revision
    else:
        return "dev"


@pytest.fixture(scope="session")
def testclient(github_token, api_url):
    with requests.session() as session:
        response = session.get(
            f"{api_url}/auth/token-login",
            headers={"Authorization": f"Bearer {github_token}"},
        )
        response.raise_for_status()
        yield session
