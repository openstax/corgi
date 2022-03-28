import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C618754")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_e2e_pdf_git_jobs(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Clicks the PDF(git) button
    home.click_pdf_git_radio_button()

    # AND: Correct data are typed into the input fields
    home.fill_collection_id_field("osbooks-contemporary-math/contemporary-math")
    home.fill_version_field("latest")
    home.fill_style_field("contemporary-math")

    # AND: Create button is clicked
    home.click_create_button()

    # THEN: The home closes and job is queued
    assert home.create_new_job_button_is_visible
    assert "queued" in home.status_message.text_content()
