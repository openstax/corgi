import pytest

from pages.home import Home


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_modal_remains_open_with_data_fields_empty(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()
    # AND: The create new pdf button is clicked
    modal = home.click_create_new_pdf_button()

    # AND: Create button is clicked when data fields are empty
    modal.click_create_button()

    # THEN: The create new pdf modal stays open
    assert home.create_pdf_modal_is_open


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "colid, vers, style, serv", [("col26069", "latest", "chemistry", "staging")]
)
def test_modal_create_pdf_cancel(selenium, base_url, colid, vers, style, serv):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # AND: Modal window opens
    modal = home.click_create_new_pdf_button()

    # AND: Data is entered into the four fields
    modal.fill_collection_id_field(colid)
    modal.fill_version_field(vers)
    modal.fill_style_field(style)
    modal.fill_server_field(serv)

    # AND: Cancel button is clicked
    modal.click_cancel_button()

    # THEN: The modal window closes
    assert home.create_pdf_modal_is_closed
    assert home.is_create_new_pdf_button_displayed
