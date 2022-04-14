import pytest
import requests

ENDPOINT = "version"


@pytest.mark.integration
def test_version_get_request(api_url, tag, stack_name, revision, deployed_at):
    # GIVEN: An api url to the version endpoint
    url = f"{api_url}/{ENDPOINT}"

    # WHEN: A GET request is made to the url
    response = requests.get(url)

    assert response.status_code == 200

    response_json = response.json()

    # THEN: A proper response is returned
    assert response_json == {"stack_name": stack_name,
                             "revision": revision,
                             "tag": tag,
                             "deployed_at": deployed_at
                            }
