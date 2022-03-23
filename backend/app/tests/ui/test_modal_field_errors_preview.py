import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C624696")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_invalid_colid_error_preview(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Clicks the Web Preview button
    home.click_web_preview_radio_button()

    # AND: Incorrect collection id is typed into the collection id field
    home.fill_collection_id_field("1col11229")

    # AND: Create button is clicked
    home.click_create_button()

    # THEN: Correct error message appears in collection id field
    assert (
        "A valid collection ID is required, e.g. col12345"
        == home.collection_id_field_texts.text_content()
    )

    assert "Style is required" == home.style_field_texts.text_content()

    assert "Please select a server" == home.content_server_field_texts.text_content()

    # THEN: The home does not close and remains open
    assert home.create_job_modal_is_open


@pytestrail.case("C646766")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_invalid_colid_error_git_preview(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Web preview (git) button is clicked
    home.click_web_preview_git_radio_button()

    # AND: Create button is clicked when data fields are empty
    home.click_create_button()

    # THEN: Correct error message appears in collection id and style field
    assert "Repo and slug are required" == home.collection_id_field_texts.text_content()

    assert "Style is required" == home.style_field_texts.text_content()

    # THEN: No error message appears for Content Server as it is disabled for web preview git
    assert (
        "Please select a server" not in home.content_server_field_texts.text_content()
    )

    # AND: Collection ID field has incorrect colid
    home.fill_collection_id_field(
        "osbooks_fizyka_bundle1/fizyka=dla-szkół-wyższych-tom-1"
    )

    # THEN: Correct error message appears in collection id and style field
    assert (
        "A valid repo and slug name is required, e.g. repo-name/slug-name"
        == home.collection_id_field_texts.text_content()
    )

    assert "Style is required" == home.style_field_texts.text_content()
