import json

import pytest
import requests

ENDPOINT = "jobs"


@pytest.mark.integration
def test_jobs_post_and_get_request_successful(api_url):
    # GIVEN: An api url to the jobs endpoint
    # AND: Data for job is ready to be submitted.
    url = f"{api_url}/{ENDPOINT}/"
    data = {
        "collection_id": "abc123",
        "status_id": "1",
        "content_server_id": "1",
        "job_type_id": "1"
    }

    # WHEN: A POST request is made to the url with data
    response = requests.post(url, data=json.dumps(data))

    # THEN: A 200 code is returned
    # AND: Correct attributes of the request exist in the response
    assert response.status_code == 200

    response = response.json()

    assert response["collection_id"] == "abc123"
    assert response["content_server"]["hostname"] == "content01.cnx.org"
    assert response["status"]["name"] == "queued"
    assert response["job_type"]["name"] == "pdf"
    
    # AND: We can retrieve that job from the backend.
    job_id = response["id"]
    job_url = f"{url}{job_id}"
    job_response = requests.get(job_url)

    assert job_response.status_code == 200

    job_data = job_response.json()

    assert job_data["id"] == job_id
    assert job_data["content_server"]["hostname"] == "content01.cnx.org"
    assert job_data["status"]["name"] == "queued"
    assert job_data["job_type"]["name"] == "pdf"
