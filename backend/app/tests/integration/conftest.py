import pytest


@pytest.fixture(scope="module")
def api_url(base_url):
    return f"{base_url}/api"
