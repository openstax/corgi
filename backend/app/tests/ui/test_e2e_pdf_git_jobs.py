import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi

import requests


@pytestrail.case("C618754")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "colid, version, style",
    [("osbooks-astronomy/astronomy-2e", "latest", "astronomy")],
)
def test_e2e_pdf_git_jobs(api_url, chrome_page, corgi_base_url, colid, version, style):
    # GIVEN: Playwright, chromium and the corgi_base_url
    url = f"{api_url}/jobs/"

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

    # AND: Create button is clicked
    home.remove_focus()
    home.click_create_button()

    # AND: Data from latest job are collected
    r = requests.get(url)

    if r.status_code != 200:
        pytest.fail(f"Response to {url} did not return 200 code as expected!")

    response_json = r.json()

    latest_job = max(response_json, key=lambda ev: ev['id'])

    colid_latest = latest_job["collection_id"]
    status_latest = latest_job["status"]["name"]
    job_id_latest = latest_job["id"]

    if job_id_latest and colid_latest == colid:

        # THEN: The home closes and job is queued
        assert home.create_new_job_button_is_visible
        assert status_latest == home.status_message.inner_text()

    else:
        pytest.fail("Something failed here...")
