import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C606121")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_e2e_pdf_jobs(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: PDF radio button is automatically selected and correct data are typed into the input fields
    home.fill_collection_id_field("col11992")
    home.fill_version_field("1.9")
    home.fill_style_field("astronomy")
    home.click_content_server()
    home.click_content_server_dropdown("qa")

    # AND: Create button is clicked
    home.click_create_button()

    # THEN: The modal closes and job is queued
    assert home.create_new_job_button_is_visible
    assert "queued" in home.status_message.text_content()
