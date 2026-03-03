import pytest
from pytest_testrail.plugin import pytestrail

from tests.ui.pages.home import HomeCorgi


@pytestrail.case("C593561")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_home_page_loads(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The home page UI elements are visible
    assert home.book_input_fields
    assert home.job_types_check_boxes
    assert home.jobs_data_table
    assert home.jobs_pagination_box
    assert home.show_abl_link_is_visible


@pytestrail.case("C624693")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_new_job_button_is_disabled(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: Create new job button is initially disabled
    assert not home.create_new_job_button_is_enabled


@pytest.mark.ui
@pytest.mark.nondestructive
def test_pipeline_versions_button_is_visible(chrome_page, corgi_base_url):
    # GIVEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The Pipeline Versions button is visible
    assert home.pipeline_versions_button_is_visible


@pytest.mark.ui
@pytest.mark.nondestructive
def test_pipeline_version_dialog_opens_and_closes(chrome_page, corgi_base_url):
    # GIVEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: The Pipeline Versions button is clicked
    home.click_pipeline_versions_button()

    # THEN: The dialog is visible with 3 slot rows
    assert home.pipeline_version_dialog_is_visible
    assert home.pipeline_version_dialog_slot_rows.count() == 3

    # WHEN: The dialog is closed
    home.click_pipeline_version_dialog_close_button()

    # THEN: The dialog is no longer visible
    assert not home.pipeline_version_dialog_is_visible


@pytestrail.case("C624694")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astronomy-2e", "main")],
)
def test_create_new_job_button_is_enabled(
    chrome_page, corgi_base_url, repo, book, version
):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_epub_job_option()

    # THEN: Create new job button is enabled
    assert home.create_new_job_button_is_enabled
