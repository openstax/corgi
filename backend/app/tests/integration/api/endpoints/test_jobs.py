from pathlib import Path

import pytest


ENDPOINT = "jobs"


@pytest.mark.integration
@pytest.mark.parametrize(
    "status_id, job_type_id, version, repo_name, repo_owner, book_name",
    [("1", "3", None, "tiny-book", "openstax", "book-slug1"),
     ("1", "4", None, "tiny-book", "openstax", "book-slug1")])
def test_jobs_cru(
        testclient,
        api_url,
        status_id,
        job_type_id,
        version,
        repo_owner,
        repo_name,
        book_name):
    # GIVEN: An api url to the jobs endpoint
    # AND: Data for job is ready to be submitted.
    data = {
        "status_id": status_id,
        "job_type_id": job_type_id,
        "version": version,
        "repository": {
            "name": repo_name,
            "owner": repo_owner
        },
        "book": book_name
    }

    # WHEN: A POST request is made to the url with data
    response = testclient.post(f"{api_url}/{ENDPOINT}/", json=data)

    # THEN: A 200 code is returned
    assert response.status_code == 200
    job = response.json()
    
    # AND: Correct attributes of the request exist in the response
    assert job["status_id"] == status_id
    assert job["job_type_id"] == job_type_id
    assert isinstance(job.get("version", None), str)

    # AND: We can retrieve that job from the backend.
    job_id = job["id"]
    job_response = testclient.get(f"{api_url}/{ENDPOINT}/{job_id}")
    assert job_response.status_code == 200
    job_data = job_response.json()
    assert job_data["id"] == job_id
    assert job_data["status_id"] == status_id
    assert job_data["job_type_id"] == job_type_id
    user_data = job_data.get("user", None)
    assert isinstance(user_data, dict)
    assert "name" in user_data
    assert "avatar_url" in user_data
    assert "id" in user_data

    # WHEN: A PUT request is made to the url with data
    updated_status_id = "4"
    error_text = "Generated by integration test"
    data = {
        "status_id": updated_status_id,
        "error_message": error_text
    }
    job_update_response = testclient.put(f"{api_url}/{ENDPOINT}/{job_id}",
                                         json=data)
    
    # THEN: A 200 code is returned
    assert job_update_response.status_code == 200
    updated_job_data = job_update_response.json()

    # AND: Correct attributes of the request exist in the response
    assert updated_job_data["id"] == job_id
    assert updated_job_data["status_id"] == updated_status_id

    # AND: Only what we updated has changed
    job_response = testclient.get(f"{api_url}/{ENDPOINT}/{job_id}")
    assert job_response.status_code == 200
    job_data = job_response.json()
    assert job_data["status_id"] == updated_status_id
    assert job_data["id"] == job_id    
    assert job_data["job_type_id"] == job_type_id
    user_data = job_data.get("user", None)
    assert isinstance(user_data, dict)
    assert "name" in user_data
    assert "avatar_url" in user_data
    assert "id" in user_data

    # WHEN: We retrieve the error text 
    error_text_response = testclient.get(f"{api_url}/{ENDPOINT}/error/{job_id}")

    # THEN: A 200 code is returned
    assert error_text_response.status_code == 200
    error_text_from_server = error_text_response.json()

    # AND: We get the error as a string
    assert error_text == error_text_from_server
