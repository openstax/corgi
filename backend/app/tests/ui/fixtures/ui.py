from playwright.sync_api import sync_playwright
import pytest


@pytest.fixture
def chrome_page():
    """Return playwright chromium browser page"""
    playwright_sync = sync_playwright().start()
    chrome_browser = playwright_sync.chromium.launch(
        headless=True, slow_mo=1000, timeout=99999
    )
    page = chrome_browser.new_page()
    yield page

    chrome_browser.close()
    playwright_sync.stop()


@pytest.fixture
def corgi_base_url():
    """Return local corgi url"""
    corgi_base_url = "http://frontend"
    return corgi_base_url
