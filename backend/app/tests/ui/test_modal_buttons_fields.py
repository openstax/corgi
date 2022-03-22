import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C624697")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_modal_radio_buttons(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # THEN: The pdf, web preview, pdf(git) and web preview (git) radio buttons are displayed
    assert home.pdf_radio_button
    assert home.web_preview_radio_button
    assert home.pdf_git_radio_button
    assert home.web_preview_git_radio_button


@pytestrail.case("C646763")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_modal_input_fields(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # THEN: The Collection ID, Version, Style and Content Server input fields are displayed
    assert home.collection_id_field
    assert home.version_field
    assert home.style_field
    assert home.server_field


@pytestrail.case("C646763")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_modal_cancel_create_buttons(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # THEN: The Cancel and Create buttons are displayed
    assert home.modal_cancel_button_is_visible
    assert home.create_button_is_visible

    # AND: The Hint text is visible
    assert (
        "Hint: You can also edit the style field yourself"
        in home.modal_hint_text.text_content()
    )
