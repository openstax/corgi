from playwright.sync_api import sync_playwright
import pytest


@pytest.fixture
def chrome_browser():

    playwright_sync = sync_playwright().start()
    chromebrowser = playwright_sync.chromium.launch(headless=False, slow_mo=1000)

    return chromebrowser


@pytest.fixture
def chrome_page(chrome_browser):
    context = chrome_browser.new_context()
    page = context.new_page()

    return page
