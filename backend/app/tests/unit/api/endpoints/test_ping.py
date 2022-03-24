import pytest

ENDPOINT = "ping"


@pytest.mark.unit
@pytest.mark.nondestructive
def test_ping_get_request(testclient):
    # GIVEN: a test client and a URL
    url = f"/api/{ENDPOINT}"

    # WHEN: A GET request is made to the endpoint
    response = testclient.get(url)

    # THEN: A proper response is returned
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
