import requests

ENDPOINT = "jobs"


def test_jobs_get_request(api_url):
    # GIVEN: An api url to the jobs endpoint
    url = f"{api_url}/{ENDPOINT}"

    # WHEN: A GET request is made to the url
    response = requests.get(url)

    # THEN: A proper response is returned
    assert response.json() == []
