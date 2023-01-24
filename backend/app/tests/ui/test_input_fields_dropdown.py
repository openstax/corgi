import pytest
from pytest_testrail.plugin import pytestrail

from tests.ui.pages.home import HomeCorgi


@pytestrail.case("C646767")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_repo_field_dropdown_is_visible(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Repo field is clicked
    home.click_repo_field()

    # THEN: Repo dropdown opens
    assert home.repo_dropdown_is_visible


@pytestrail.case("C646767")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_book_field_dropdown_is_visible(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Book field is clicked
    home.click_book_field()

    # THEN: Book dropdown opens
    assert home.book_dropdown_is_visible


@pytestrail.case("C646767")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_version_field_dropdown_is_visible(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Version field is clicked
    home.click_version_field()

    # THEN: Version dropdown opens
    assert home.version_dropdown_is_visible
