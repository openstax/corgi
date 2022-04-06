import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C624695")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize("colid", ["1col11992"])
def test_invalid_pdf_colid_error(chrome_page, corgi_base_url, colid):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: PDF button is clicked
    home.click_pdf_radio_button()

    # AND: Incorrect collection id is typed into the collection id field
    home.fill_collection_id_field(colid)

    # AND: Create button is clicked
    home.click_create_button()

    # THEN: Correct error message appears in collection id field
    assert (
        "A valid collection ID is required, e.g. col12345"
        == home.collection_id_field_texts.text_content()
    )

    assert "Style is required" == home.style_field_texts.text_content()

    assert "Please select a server" == home.content_server_field_texts.text_content()

    # THEN: The home does not close and remains open
    assert home.create_job_modal_is_open


@pytestrail.case("C624695")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "colid1, colid2",
    [
        (
            "osbooks_fizyka_bundle2/fizyka-dla-szkół-wyższych-tom-1",
            "osbooks_fizyka_bundle1/fizyka=dla-szkół-wyższych-tom-1",
        )
    ],
)
def test_invalid_git_colid_error(chrome_page, corgi_base_url, colid1, colid2):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: PDF(git) button is clicked
    home.click_pdf_git_radio_button()

    # AND: Create button is clicked when data fields are empty and collection ID field has incorrect colid
    home.click_create_button()

    # THEN: Correct error message appears in collection id and style field
    assert "Repo and slug are required" == home.collection_id_field_texts.text_content()

    # Test unicode book collection (here Polish)
    home.fill_collection_id_field(colid1)

    assert "e.g. repo-name/slug-name" == home.collection_id_field_texts.text_content()

    # Unallowed characters
    home.fill_collection_id_field(colid2)

    assert (
        "A valid repo and slug name is required, e.g. repo-name/slug-name"
        == home.collection_id_field_texts.text_content()
    )

    assert "Style is required" == home.style_field_texts.text_content()

    # THEN: No error message appears for Content Server as it is disabled for pdf git
    assert (
        "Please select a server" not in home.content_server_field_texts.text_content()
    )
