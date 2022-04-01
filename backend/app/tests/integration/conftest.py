import os

import pytest



# Get values we need to setup the environment from the command line or through env vars
def pytest_addoption(parser):
    group = parser.getgroup("corgi", "corgi")
    group.addoption(
        "--stack-name",
        default=os.getenv("STACK_NAME", "dev"),
        help="The name of the stack, used in the version endpoint",
    )
    parser.addoption(
        "--revision",
        default=os.getenv("REVISION", "dev"),
        help="The sha/revision of CORGI deployed",
    )
    parser.addoption(
        "--deployed_at",
        default=os.getenv("DEPLOYED_AT", "dev"),
        help="The timestamp CORGI was deployed",
    )
    parser.addoption(
        "--tag",
        default=os.getenv("TAG", "dev"),
        help="The tag used on the images",
    )
    
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
    """Return the tag"""
    config = request.config
    stack_name = config.getoption("stack_name")
    if stack_name is not None:
        return stack_name
    else:
        return "dev"


@pytest.fixture(scope="session")
def revision(request):
    """Return the tag"""
    config = request.config
    stack_name = config.getoption("revision")
    if revision is not None:
        return revision
    else:
        return "dev"

@pytest.fixture(scope="session")
def deployed_at(request):
    """Return the deployed_at timestamp"""
    config = request.config
    deployed_at = config.getoption("deployed_at")
    if deployed_at is not None:
        return deployed_at
    else:
        return "dev"
