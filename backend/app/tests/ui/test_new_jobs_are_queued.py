from pytest_testrail.plugin import pytestrail

from tests.ui.pages.home import HomeCorgi

import pytest


@pytestrail.case("C651147")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-otto-book", "ottó-book", "main")],
)
def test_job_id_dialog_opens_closes(chrome_page_slow, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_webview_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and job ID is clickable
    if home.elapsed_time.inner_text() <= '00:00:07' and home.queued_job_type == "Web Preview (git)":

        home.click_job_id()

        assert home.job_id_dialog_is_visible
        assert home.job_id.inner_text() in home.job_id_dialog_title.inner_text()

        home.click_job_id_dialog_close_button()
        assert not home.job_id_dialog_is_visible

    else:
        pytest.fail(f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}")


@pytestrail.case("C655443")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_version_sha_is_clickable(chrome_page_slow, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    # THEN: A new job's version sha is clickable
    if home.latest_job_status == 'completed':

        with chrome_page_slow.context.expect_page() as tab:
            home.click_version_sha()

        new_tab = tab.value

        assert home.queued_repo_name.inner_text() in new_tab.url

    else:
        pytest.fail(f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}")
