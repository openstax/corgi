from tests.ui.pages.home import HomeCorgi, JobStatus
import pytest

from bs4 import BeautifulSoup

import requests


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, version",
    [("osbooks-otto-book", "main")],
)
def test_e2e_webview_bundle_jobs_urls(chrome_page_slow, corgi_base_url, repo, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    current_job_id = home.next_job_id

    # WHEN: Input fields are filled (not book field) and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_version_field(version)

    home.click_webview_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and verified
    home.wait_for_job_created(current_job_id)
    home.wait_for_job_status(JobStatus.COMPLETED)

    if home.queued_job_type == "Web Preview (git)":
        home.click_job_type_icon()

        assert home.job_type_icon_job_links_are_visible

        ccont = chrome_page_slow.content()

        sopa = BeautifulSoup(ccont, "html.parser")
        books = sopa.select("div[class*=mdc-dialog__content]")

        book_titles = []
        book_hrefs = []

        for book in books:
            atags = book.find_all("a")
            for atag in atags:
                book_titles.append(atag.text)
                book_hrefs.append(atag["href"])

        for bhref in book_hrefs:
            reqs = requests.head(bhref)
            assert reqs.status_code == 200

            assert home.worker_version.inner_text() in bhref

    else:
        pytest.fail(
            f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}"
        )
