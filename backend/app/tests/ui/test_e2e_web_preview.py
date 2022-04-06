import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C614652")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "colid, style, server", [("col11992", "astronomy", "staging")],
)
def test_e2e_web_preview_jobs(chrome_page, corgi_base_url, colid, style, server):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Clicks the Web Preview button
    home.click_web_preview_radio_button()

    # AND: Correct data are typed into the input fields
    home.fill_collection_id_field(colid)
    home.fill_style_field(style)
    home.click_content_server()
    home.click_content_server_dropdown(server)

    # AND: Create button is clicked
    home.click_create_button()

    # THEN: The home closes and job is queued
    assert home.create_new_job_button_is_visible
    assert "queued" in home.status_message.text_content()
