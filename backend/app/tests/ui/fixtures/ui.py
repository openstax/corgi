from playwright.sync_api import sync_playwright
import pytest

import requests


@pytest.fixture(scope="session")
def session_cookie(request, api_url):
    config = request.config

    github_token = config.getoption("--github-token")
    assert isinstance(github_token, str) and len(github_token) > 0, \
        ("Use option --github-token or env var GITHUB_TOKEN to set the"
         "token to use")
    response = requests.get(f"{api_url}/auth/token-login",
                            headers={"Authorization": f"Bearer {github_token}"})
    response.raise_for_status()

    session_cookie = response.cookies.get("session", None)
    assert session_cookie is not None, "Could not get session cookie"

    return session_cookie


@pytest.fixture(scope="session")
def additional_headers(session_cookie):
    return {
        "Cookie": f"session={session_cookie}"
    }


@pytest.fixture
def chrome_page(additional_headers):
    """Return playwright chromium browser page"""
    playwright_sync = sync_playwright().start()
    chrome_browser = playwright_sync.chromium.launch(
        headless=True, slow_mo=800, timeout=120000
    )
    context = chrome_browser.new_context()
    context.set_extra_http_headers(additional_headers)

    page = context.new_page()
    yield page

    chrome_browser.close()
    playwright_sync.stop()


@pytest.fixture
def chrome_page_slow(additional_headers):
    """Return playwright chromium browser page - slow flow"""
    playwright_sync = sync_playwright().start()
    chrome_browser = playwright_sync.chromium.launch(
        headless=True, slow_mo=4100, timeout=120000
    )
    context = chrome_browser.new_context()
    context.set_extra_http_headers(additional_headers)

    page = context.new_page()
    yield page

    chrome_browser.close()
    playwright_sync.stop()


@pytest.fixture
def corgi_base_url(base_url):
    """Return local corgi url"""
    return base_url
