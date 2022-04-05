import pytest
import requests

ENDPOINT = "version"


@pytest.mark.integration
@pytest.mark.nondestructive
def test_version_get_request(api_url, stack_name, tag):
    # GIVEN: An api url to the version endpoint
    url = f"{api_url}/{ENDPOINT}"

    # WHEN: A GET request is made to the url
    response = requests.get(url)

    version_data = response.json()

    # THEN: A proper response is returned
    assert version_data["stack_name"] == stack_name
    assert version_data["tag"] == tag
