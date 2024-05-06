import pytest
import requests

from tests.utils import validate_datetime

ENDPOINT = "version"


@pytest.mark.integration
@pytest.mark.nondestructive
def test_version_get_request(api_url, tag, stack_name, revision):
    # GIVEN: An api url to the version endpoint
    url = f"{api_url}/{ENDPOINT}"

    # WHEN: A GET request is made to the url and returns 200 code
    response = requests.get(url)

    assert response.status_code == 200

    response_json = response.json()

    # THEN: The response attributes are correct
    assert response_json["stack_name"] == stack_name
    assert response_json["revision"] == revision
    assert response_json["tag"] == tag
    assert validate_datetime(response_json["deployed_at"])
