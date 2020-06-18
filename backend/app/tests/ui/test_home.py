import pytest

from pages.home import Home


@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_new_pdf_button_is_displayed(selenium, base_url):
    # GIVEN: Selenium driver and the base_url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # THEN: The create new pdf button is displayed
    assert home.is_create_new_job_button_displayed


@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_pdf_job_modal_form_opens_and_closes(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    # AND: The create new pdf button is clicked
    home = Home(selenium, base_url).open()
    modal = home.click_create_new_job_button()

    # THEN: The create new pdf modal opens
    # AND:  The modal closes when cancel is clicked
    assert home.create_job_modal_is_open

    modal.click_cancel_button()
    assert not home.create_job_modal_is_open
