import pytest
from bs4 import BeautifulSoup

from tests.ui.pages.home import HomeCorgi

"""After all corgi UI tests are completed, all running jobs are aborted"""


@pytest.mark.nondestructive
def test_zzz_abort_jobs(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    ccont = chrome_page.content()
    home = HomeCorgi(chrome_page)

    # THEN: Elements are found
    job_stats = ["processing", "queued"]

    sopa = BeautifulSoup(ccont, "html.parser")
    table = sopa.find("tbody")

    for row in range(len(table)):
        job_ids_ind = home.job_ids(row)

        if home.job_statuses(row) in job_stats:
            job_ids_ind.click()
            home.click_abort_button()

        else:
            pass
