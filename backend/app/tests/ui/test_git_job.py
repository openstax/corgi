import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "colid, version, style",
    [("osbooks-astronomy/astronomy-2e", "latest", "statistics")],
)
def test_git_job(chrome_page, corgi_base_url, colid, version, style):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # THEN: The create a new job button is clicked
    home.click_create_new_job_button()

    # AND: Clicks the PDF(git) button
    home.click_pdf_git_radio_button()

    # AND: Correct data are typed into the input fields
    home.fill_collection_id_field(colid)
    home.fill_version_field(version)
    home.fill_style_field(style)

    chrome_page.keyboard.down("Tab")
    chrome_page.keyboard.down("Tab")

    # AND: Create button is clicked
    home.click_create_button()

    home.start_date_time.wait_for()
    home.job_state_completed.wait_for()
    home.git_view_link.wait_for()

    job_id = home.job_id_locator.text_content()

    with chrome_page.expect_popup() as popup_info:
        home.git_view_link.click()

    popup = popup_info.value
    popup.wait_for_load_state()

    assert popup.locator("text=Contents") and popup.locator("text=Preface")
    assert job_id and ".pdf" in popup.url
