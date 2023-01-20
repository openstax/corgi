import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C593561")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_input_fields_are_visible(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: Input fields are visible
    assert home.repo_field
    assert home.book_field
    assert home.version_field


@pytestrail.case("C593561")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_check_boxes_are_visible(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: Job option checkboxes are visible
    assert home.pdf_job_option
    assert home.webview_job_option
    assert home.epub_job_option
    assert home.docx_job_option
