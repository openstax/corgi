import pytest

from pages.home import Home

from time import sleep


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_incorrect_col_id_error(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # AND: The create new pdf button and collection id fields are clicked
    modal = home.click_create_new_job_button()

    sleep(2)

    modal.fill_collection_id_field("f3_hhhp0")

    sleep(2)

    # AND: Create button is clicked when data fields are empty
    modal.click_create_button()

    split_col_id_incorrect = modal.collection_id_incorrect_field_error.text.splitlines()
    text_col_id_incorrect = split_col_id_incorrect[1]
    assert "A valid collection ID is required, e.g. col12345" == text_col_id_incorrect

    # AND: The modal does not close and remains open
    assert home.create_job_modal_is_open
