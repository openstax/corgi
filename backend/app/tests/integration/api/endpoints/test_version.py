import pytest
import requests

ENDPOINT = "version"


@pytest.mark.integration
@pytest.mark.nondestructive
def test_version_get_request(api_url, stack_name, revision, tag, deployed_at):
    # GIVEN: An api url to the version endpoint
    url = f"{api_url}/{ENDPOINT}"

    # WHEN: A GET request is made to the url
    response = requests.get(url)

    # THEN: A proper response is returned
    assert response.json() == {"stack_name": stack_name,
                               "revision": revision,
                               "tag": tag,
                               "deployed_at": deployed_at
                               }
