import pytest

from pages.home import Home


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_pdf_and_preview_radio_buttons(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # AND: The create new pdf button is clicked
    modal = home.click_create_new_job_button()

    # THEN: The the pdf and distribution preview radio buttons are displayed
    assert modal.is_pdf_radio_button_displayed
    assert modal.is_preview_radio_button_displayed


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_e2e_cops_preview_jobs(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # AND: The create new pdf button is clicked
    modal = home.click_create_new_job_button()

    # AND: Clicks the Distribution Preview button
    modal.click_distribution_preview_radio_button()

    # AND: Correct data are typed into the input fields
    modal.fill_collection_id_field("col11992")
    modal.fill_version_field("1.9")
    modal.fill_style_field("astronomy")
    modal.fill_server_field("qa")

    # AND: Create button is clicked
    modal.click_create_button()
    modal.click_create_button()

    # THEN: The modal does not close and remains open
    assert home.is_create_new_job_button_displayed
    assert modal.status_message.text == "queued"
