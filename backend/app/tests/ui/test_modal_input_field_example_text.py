import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C646767")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_modal_input_field_example_text_pdf(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job and pdf radio button is clicked
    home.click_create_new_job_button()
    home.click_pdf_radio_button()

    # AND: Correct data are typed into the fields (or just clicked)
    home.fill_collection_id_field("col11992")

    # THEN: Correct example message appears under collection id field
    assert "e.g. col12345" == home.collection_id_field_texts.text_content()

    home.fill_version_field("1.9")

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
def test_modal_input_field_example_text_git(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked and git preview radio button is clicked
    home.click_create_new_job_button()
    home.click_web_preview_git_radio_button()

    # AND: Correct data are typed into the fields (or just clicked)
    home.fill_collection_id_field(
        "osbooks-introduction-philosophy/introduction-philosophy"
    )

    # THEN: Correct example message appears under collection id field
    assert "e.g. repo-name/slug-name" == home.collection_id_field_texts.text_content()

    home.fill_version_field("latest")

    # THEN: Correct example message appears under version field
    assert "e.g. master or a git tag" == home.version_field_texts.text_content()

    home.click_style_field()

    # THEN: Correct example message appears under style field and style dropdown opens
    assert "e.g. microbiology" == home.style_field_texts.text_content()
    assert home.style_field_dropdown
