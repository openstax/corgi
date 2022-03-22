import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C624693")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_new_job_button_is_visible(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is visible
    assert home.create_new_job_button_is_visible


@pytestrail.case("C624694")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_new_job_modal_form_opens_and_closes(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job modal is open
    home.click_create_new_job_button()
    assert home.modal_cancel_button_is_visible

    # THEN: The create a new job modal is closed
    home.click_modal_cancel_button()
    assert home.create_new_job_button_is_visible
