import pytest

from pages.home import Home

from time import sleep


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_e2e_cops_jobs(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # AND: The create new pdf button is clicked
    modal = home.click_create_new_job_button()

    # AND: Incorrect collection id is typed into the collection id field
    modal.fill_collection_id_field("col11992")
    modal.fill_version_field("1.9")
    modal.fill_style_field("astronomy")
    modal.fill_server_field("qa")

    sleep(2)

    # AND: Create button is clicked
    modal.click_create_button()
    sleep(2)
    modal.click_create_button()

    sleep(6)

    # THEN: The modal does not close and remains open
    assert home.is_create_new_job_button_displayed
    assert modal.status_message.text == "assigned"
