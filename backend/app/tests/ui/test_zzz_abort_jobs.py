from tests.ui.pages.home import HomeCorgi

import pytest

from bs4 import BeautifulSoup

"""After all corgi UI tests are completed, all running jobs are aborted"""


@pytest.mark.nondestructive
def test_zzz_abort_jobs(chrome_page, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    ccont = chrome_page.content()
    home = HomeCorgi(chrome_page)

    # THEN: Elements are found
    sopa = BeautifulSoup(ccont, 'html.parser')

    rows = []
    job_stats = ["processing", "queued"]

    for table in sopa.find_all('tbody'):
        for row in table:
            rows.append(row.find_all_next('tr'))

    # THEN: Running jobs are aborted
    for i in range(len(rows)):
        job_ids_ind = home.job_ids(i)

        if home.job_statuses(i) in job_stats:
            job_ids_ind.click()
            home.click_abort_button()

        else:
            pass
