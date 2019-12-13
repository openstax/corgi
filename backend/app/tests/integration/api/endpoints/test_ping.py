import requests


def test_ping_get_request(api_url):
    endpoint = "ping"
    url = f"{api_url}/{endpoint}"
    response = requests.get(url)
    assert response.json() == {'message': 'pong'}
