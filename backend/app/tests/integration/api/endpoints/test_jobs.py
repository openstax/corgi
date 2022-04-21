import json

import pytest
import requests

ENDPOINT = "jobs"


@pytest.mark.integration
@pytest.mark.parametrize(
    "colid, status_id, content_server_id, job_type_id",
    [("osbooks-contemporary-math/contemporary-math", "1", "1", "1")],
)
def test_jobs_post_and_get_request_successful(api_url, colid, status_id, content_server_id, job_type_id):
    # GIVEN: An api url to the jobs endpoint
    # AND: Data for job is ready to be submitted.
    url = f"{api_url}/{ENDPOINT}/"
    data = {
        "collection_id": colid,
        "status_id": status_id,
        "content_server_id": content_server_id,
        "job_type_id": job_type_id
    }

    # WHEN: A POST request is made to the url with data
    response = requests.post(url, data=json.dumps(data))

    # THEN: A 200 code is returned
    # AND: Correct attributes of the request exist in the response
    assert response.status_code == 200

    response = response.json()

    assert response["collection_id"] == colid
    assert response["content_server"]["id"] == content_server_id
    assert response["status"]["id"] == status_id
    assert response["job_type"]["id"] == job_type_id
    
    # AND: We can retrieve that job from the backend.
    job_id = response["id"]
    job_url = f"{url}{job_id}"
    job_response = requests.get(job_url)

    assert job_response.status_code == 200

    job_data = job_response.json()

    assert job_data["id"] == job_id
    assert job_data["content_server"]["id"] == content_server_id
    assert job_data["status"]["id"] == status_id
    assert job_data["job_type"]["id"] == job_type_id
