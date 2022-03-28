import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C646767")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize("colid, version", [("col11992", "1.9")])
def test_modal_input_field_help_text_pdf(chrome_page, corgi_base_url, colid, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job and pdf radio button is clicked
    home.click_create_new_job_button()
    home.click_pdf_radio_button()

    # AND: Correct data are typed into the fields (or just clicked)
    home.fill_collection_id_field(colid)

    # THEN: Correct example message appears under collection id field
    assert "e.g. col12345" == home.collection_id_field_texts.text_content()

    home.fill_version_field(version)

    # THEN: Correct example message appears under version field
    assert "e.g. 19.2" == home.version_field_texts.text_content()

    home.click_style_field()

    # THEN: Correct example message appears under style field and style dropdown opens
    assert "e.g. microbiology" == home.style_field_texts.text_content()
    assert home.style_field_dropdown

    home.click_content_server()

    # THEN: Content server dropdown opens
    assert home.content_server_dropdown


@pytestrail.case("C646767")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "colid, version",
    [("osbooks-introduction-philosophy/introduction-philosophy", "latest")],
)
def test_modal_input_field_help_text_git(chrome_page, corgi_base_url, colid, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked and git preview radio button is clicked
    home.click_create_new_job_button()
    home.click_web_preview_git_radio_button()

    # AND: Correct data are typed into the fields (or just clicked)
    home.fill_collection_id_field(colid)

    # THEN: Correct example message appears under collection id field
    assert "e.g. repo-name/slug-name" == home.collection_id_field_texts.text_content()

    home.fill_version_field(version)

    # THEN: Correct example message appears under version field
    assert "e.g. master or a git tag" == home.version_field_texts.text_content()

    home.click_style_field()

    # THEN: Correct example message appears under style field and style dropdown opens
    assert "e.g. microbiology" == home.style_field_texts.text_content()
    assert home.style_field_dropdown
