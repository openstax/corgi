import pytest
from pytest_testrail.plugin import pytestrail

from tests.ui.pages.home import HomeCorgi, JobStatus


@pytestrail.case("C646763")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astronomy-2e", "main")],
)
def test_create_new_job_button_stays_enabled(chrome_page, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_docx_job_option()

    # THEN: The main UI elements are visible and create new job button is enabled
    assert home.create_new_job_button_is_enabled

    home.click_create_new_job_button()

    assert home.create_new_job_button_is_enabled
    assert not home.error_banner_is_visible


@pytestrail.case("C646766")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astronomy-2e", "")],
)
def test_create_new_job_button_enabled_disabled(chrome_page_slow, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_webview_job_option()

    # THEN: The main UI elements are visible and create new job button is enabled/disabled
    assert home.create_new_job_button_is_enabled

    home.click_create_new_job_button()

    assert home.create_new_job_button_is_enabled
    assert not home.error_banner_is_visible

    home.click_webview_job_option()

    assert not home.create_new_job_button_is_enabled

    home.click_docx_job_option()
    home.click_pdf_job_option()

    assert home.create_new_job_button_is_enabled

    home.click_job_id()
    home.click_abort_button()

    home.wait_for_job_status(JobStatus.ABORTED, 60 * 5)


@pytest.mark.ui
@pytest.mark.nondestructive
def test_click_input_fields_only_create_new_job_button_is_disabled(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.click_repo_field()
    home.click_book_field()
    home.click_version_field()

    home.click_webview_job_option()

    # THEN: The main UI elements are visible and create new job button is disabled
    assert not home.create_new_job_button_is_enabled


@pytestrail.case("C646766")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book",
    [("osbooks-astronomy", "astronomy-2e")],
)
def test_click_input_fields_then_fill_create_new_job_button_gets_enabled(chrome_page, corgi_base_url, repo, book):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.click_repo_field()
    home.click_book_field()
    home.click_version_field()

    home.click_webview_job_option()

    # THEN: The main UI elements are visible and create new job button is disabled/enabled
    assert not home.create_new_job_button_is_enabled

    home.fill_book_field(book)
    home.fill_repo_field(repo)

    home.click_docx_job_option()

    assert home.create_new_job_button_is_enabled


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astronomy-2e", "main")],
)
def test_book_field_empty_create_new_job_button_disabled(chrome_page, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_version_field(version)

    home.click_epub_job_option()
    home.click_docx_job_option()

    # THEN: The main UI elements are visible and create new job button is disabled
    assert not home.create_new_job_button_is_enabled

    home.fill_repo_field(" ")
    home.fill_book_field(book)
    home.fill_version_field(" ")

    assert not home.create_new_job_button_is_enabled


@pytestrail.case("C598227")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book",
    [("osbooks-astronomy", "astronomy-2e")],
)
def test_space_character_create_new_job_button_disabled(chrome_page, corgi_base_url, repo, book):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(" ")
    home.fill_book_field(" ")

    home.click_webview_job_option()
    home.click_pdf_job_option()

    # THEN: The main UI elements are visible and create new job button is disabled/enabled
    assert not home.create_new_job_button_is_enabled

    home.fill_book_field(book)
    home.fill_repo_field(repo)

    assert home.create_new_job_button_is_enabled

    home.fill_book_field(" ")

    assert not home.create_new_job_button_is_enabled
