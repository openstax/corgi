import pytest

from pages.home import Home


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_new_pdf_button_is_displayed(selenium, base_url):
    # GIVEN: Selenium driver and the base_url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # THEN: The create new pdf button is displayed
    assert home.is_create_new_pdf_button_displayed


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_pdf_job_modal_form_opens_and_closes(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()
    # AND: The create new pdf button is clicked
    modal = home.click_create_new_pdf_button()

    # THEN: The create new pdf modal opens
    assert home.create_pdf_modal_is_open
    # AND:  The modal closes when cancel is clicked
    modal.click_cancel_button()
    assert home.create_pdf_modal_is_closed


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_pdf_job_modal_form_remains_open_when_data_fields_empty(selenium, base_url):
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
def test_previous_page_button_is_clickable(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()
    # AND: The previous page button is clicked
    home.click_previous_page_button()

    # THEN: The home page remains open
    assert home.create_pdf_modal_is_closed
    assert home.is_create_new_pdf_button_displayed


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_next_page_button_is_clickable(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()
    # AND: The next page button is clicked
    home.click_next_page_button()

    # THEN: The home page remains open
    assert home.create_pdf_modal_is_closed
    assert home.is_create_new_pdf_button_displayed


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_go_button_is_clickable(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()
    # AND: Go button is clicked
    home.click_go_button()

    # THEN: The home page remains open
    assert home.create_pdf_modal_is_closed
    assert home.is_create_new_pdf_button_displayed


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_page_field(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()
    # AND: High value page number is entered
    home.fill_in_page('1000')
    # AND: Go button is clicked
    home.click_go_button()

    # THEN: "No data available" page opens
    assert home.no_data_available


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize("colid", ["col26069"])
@pytest.mark.parametrize("vers", ["latest"])
@pytest.mark.parametrize("style", ["chemistry"])
@pytest.mark.parametrize("serv", ["staging"])
def test_create_pdf(selenium, base_url, colid, vers, style, serv):
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
