import pytest

from pages.home import Home


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_empty_modal_field_errors(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # AND: The create new pdf button is clicked
    modal = home.click_create_new_job_button()

    # AND: Create button is clicked when data fields are empty
    modal.click_create_button()

    # THEN: The error messages are shown
    assert "Collection ID is required" == modal.collection_id_field_error.text
    assert "" == modal.version_field_error.text
    assert "Style is required" == modal.style_field_error.text
    assert "Please select a server" == modal.content_server_field_error.text

    # AND: The modal does not close and remains open
    assert home.create_job_modal_is_open
