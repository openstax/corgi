from playwright.sync_api import sync_playwright
import pytest


@pytest.fixture
def chrome_page():
    """Return playwright chromium browser page"""
    playwright_sync = sync_playwright().start()
    chrome_browser = playwright_sync.chromium.launch(
        headless=True, slow_mo=800, timeout=120000
    )
    context = chrome_browser.new_context(storage_state="state.json")

    page = context.new_page()
    yield page

    chrome_browser.close()
    playwright_sync.stop()


@pytest.fixture
def chrome_page_slow():
    """Return playwright chromium browser page - slow flow"""
    playwright_sync = sync_playwright().start()
    chrome_browser = playwright_sync.chromium.launch(
        headless=True, slow_mo=3700, timeout=120000
    )
    context = chrome_browser.new_context(storage_state="state.json")

    page = context.new_page()
    yield page

    chrome_browser.close()
    playwright_sync.stop()


@pytest.fixture
def corgi_base_url(base_url):
    """Return local corgi url"""
    base_url = "https://corgi-514.ce.openstax.org/"
    return base_url
