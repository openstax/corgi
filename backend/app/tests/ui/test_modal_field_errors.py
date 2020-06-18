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
    split_col_id = modal.collection_id_field_error.text.splitlines()
    text_col_id = split_col_id[1]
    assert "Collection ID is required" == text_col_id

    split_style = modal.style_field_error.text.splitlines()
    text_style = split_style[1]
    assert "Style is required" == text_style

    split_server = modal.content_server_field_error.text.splitlines()
    text_server = split_server[1]
    assert "Please select a server" == text_server

    # AND: The modal does not close and remains open
    assert home.create_job_modal_is_open
