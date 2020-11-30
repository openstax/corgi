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

    # THEN: The correct error messages are shown for each applicable
    # input field (colid, style and server)
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

    # WHEN: modal is open
    # AND: PDF(git) button is clicked
    modal.click_pdfgit_radio_button()

    # AND: Create button is clicked when data fields are empty
    modal.click_create_button()

    # THEN: The correct error messages are shown for each applicable
    # input field (colid and style)
    split_col_id_slug = modal.collection_id_slug_field_error.text.splitlines()
    text_col_id_slug = split_col_id_slug[1]
    assert "Repo and slug are required" == text_col_id_slug


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
def test_invalid_colid_error(selenium, base_url):
    # GIVEN: Selenium driver and the base url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # AND: The create new pdf button is clicked
    modal = home.click_create_new_job_button()

    # AND: Incorrect collection id is typed into the collection id field
    modal.fill_collection_id_field("1col11229")

    # AND: Create button is clicked
    modal.click_create_button()

    split_col_id_incorrect = modal.collection_id_incorrect_field_error.text.splitlines()
    text_col_id_incorrect = split_col_id_incorrect[1]

    # THEN: Correct error message appears in collection id field
    assert "A valid collection ID is required, e.g. col12345" == text_col_id_incorrect

    # THEN: The modal does not close and remains open
    assert home.create_job_modal_is_open

    # WHEN: modal is open and collection id has incorrect colid/slug
    # AND: PDF(git) button is clicked
    modal.click_pdfgit_radio_button()

    # AND: Create button is clicked when data fields are empty and collection ID field has incorrect colid
    modal.click_create_button()

    split_col_id_slug_incorrect = (
        modal.collection_id_slug_incorrect_field_error.text.splitlines()
    )
    text_col_id_slug_incorrect = split_col_id_slug_incorrect[1]

    # THEN: Correct error message appears in collection id and style field
    assert "repo-name/slug-name" == text_col_id_slug_incorrect

    split_style = modal.style_field_error.text.splitlines()
    text_style = split_style[1]
    assert "Style is required" == text_style
