import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C646764")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_modal_field_errors_disappear(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Create button is clicked when data fields are empty
    home.click_create_button()

    # THEN: The correct error messages are shown for each applicable
    # input field (colid, style and server)
    assert "Collection ID is required" == home.collection_id_field_texts.text_content()

    assert "Style is required" == home.style_field_texts.text_content()

    assert "Please select a server" == home.content_server_field_texts.text_content()

    # WHEN: modal is open
    # AND: PDF(git) button is clicked
    home.click_pdf_git_radio_button()

    # THEN: Error messages disappear when a different job type is clicked
    assert "" == home.collection_id_field_texts.text_content()

    assert "" == home.style_field_texts.text_content()


@pytestrail.case("C646765")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_modal_field_errors_appear_and_disappear(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Clicks the PDF(git) preview button
    home.click_web_preview_git_radio_button()

    # AND: Create button is clicked when data fields are empty
    home.click_create_button()

    # THEN: Correct error message appears in collection id and style field
    assert "Repo and slug are required" == home.collection_id_field_texts.text_content()

    assert "Style is required" == home.style_field_texts.text_content()

    # THEN: No error message appears for Content Server as it is disabled for git preview
    assert (
        "Please select a server" not in home.content_server_field_texts.text_content()
    )

    # AND: Correct data are typed into the input fields
    home.fill_collection_id_field(
        "osbooks-introduction-philosophy/introduction-philosophy"
    )
    home.fill_version_field("latest")
    home.fill_style_field("philosophy")
    chrome_page.keyboard.down("Tab")

    # THEN: Error messages disappear when correct data are input
    assert "" == home.collection_id_field_texts.text_content()
    assert "" == home.version_field_texts.text_content()
    assert "" == home.style_field_texts.text_content()
