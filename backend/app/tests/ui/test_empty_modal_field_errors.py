import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C624691")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_empty_modal_field_errors(chrome_page, corgi_base_url):
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

    # AND: The modal does not close and remains open
    assert home.create_job_modal_is_open

    # WHEN: modal is open
    # AND: PDF(git) button is clicked
    home.click_pdf_git_radio_button()

    # AND: Create button is clicked when data fields are empty
    home.click_create_button()

    # THEN: The correct error messages are shown for each applicable
    # input field (colid and style)
    assert "Repo and slug are required" == home.collection_id_field_texts.text_content()

    assert "Style is required" == home.style_field_texts.text_content()


@pytestrail.case("C624692")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_empty_modal_field_errors_preview(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Web preview button is clicked
    home.click_web_preview_radio_button()

    # AND: Create button is clicked when data fields are empty
    home.click_create_button()

    # THEN: The correct error messages are shown for each applicable
    # input field (colid, style and server)
    assert "Collection ID is required" == home.collection_id_field_texts.text_content()

    assert "Style is required" == home.style_field_texts.text_content()

    assert "Please select a server" == home.content_server_field_texts.text_content()

    # AND: The modal does not close and remains open
    assert home.create_job_modal_is_open

    # AND: Web preview (git) button is clicked
    home.click_web_preview_git_radio_button()

    # AND: Create button is clicked when data fields are empty
    home.click_create_button()

    # THEN: The correct error messages are shown for each applicable
    # input field (colid and style)
    assert "Repo and slug are required" == home.collection_id_field_texts.text_content()

    assert "Style is required" == home.style_field_texts.text_content()
