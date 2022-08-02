import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("C620213")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "colid, version, style",
    [("osbooks-introduction-philosophy/introduction-philosophy", "", "philosophy")],
)
def test_e2e_web_preview_git(chrome_page, corgi_base_url, colid, version, style):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Clicks the PDF(git) preview button
    home.click_web_preview_git_radio_button()

    # AND: Correct data are typed into the input fields
    home.fill_collection_id_field(colid)
    home.fill_version_field(version)
    home.fill_style_field(style)

    # AND: Create button is clicked
    home.remove_focus()
    home.click_create_button()

    if home.start_time_seconds_value_is_visible and home.colid_value.text_content() == "osbooks-introduction-philosophy/introduction-philosophy":

        # THEN: The home closes and job is queued
        assert home.create_new_job_button_is_visible
        assert "queued" in home.status_message.text_content()

    else:
        pytest.fail("Job was not created? Check corgi")
