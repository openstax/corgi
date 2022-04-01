import os

import pytest


@pytest.fixture(scope="module")
def api_url(base_url):
    return f"{base_url}/api"


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
    
    
