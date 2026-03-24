import pytest
from pytest_testrail.plugin import pytestrail

from tests.ui.pages.home import HomeCorgi, JobStatus


@pytestrail.case("C651147")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-otto-book", "ottó-könyv", "main")],
)
def test_job_id_dialog_opens_closes(
    chrome_page_slow, corgi_base_url, repo, book, version
):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    current_job_id = home.next_job_id

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_webview_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and verified
    home.wait_for_job_created(current_job_id)
    home.wait_for_job_status(JobStatus.COMPLETED)

    if home.queued_job_type == "Web Preview (git)":
        if home.job_type_href:
            home.click_job_id()

        else:
            raise Exception("Missing URL in job_type_href element")

        assert home.job_id_dialog_is_visible
        assert home.job_id.inner_text() in home.job_id_dialog_title.inner_text()

        home.click_job_id_dialog_close_button()
        assert not home.job_id_dialog_is_visible

    else:
        pytest.fail(
            "No new job was queued. Last job is at "
            + home.elapsed_time.inner_text()
        )


@pytestrail.case("C655443")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_version_sha_is_clickable(chrome_page_slow, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    # THEN: A new job's version sha is clickable
    with chrome_page_slow.context.expect_page() as tab:
        home.click_version_sha()

    new_tab = tab.value

    assert home.queued_repo_name.inner_text() in new_tab.url


@pytestrail.case("C655443")
@pytest.mark.ui
@pytest.mark.nondestructive
def test_show_abl_button_content(chrome_page_slow, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    # THEN: Show ABL button is clicked and page opens
    home.show_abl_button.click()

    assert home.show_abl_button_title_is_visible
    assert home.show_abl_button_table_head_is_visible


@pytest.mark.ui
@pytest.mark.nondestructive
def test_pipeline_versions_button_content(chrome_page_slow, corgi_base_url):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    # THEN: Pipeline Versions button is clicked and page opens
    home.pipeline_versions_button.click()

    assert home.pipeline_versions_dialog.is_visible()

    for label in ["Newest", "Second", "Oldest"]:
        assert label in home.pipeline_versions_codes.inner_text()

    assert home.pipeline_versions_newest_codes.count() > 0
    assert home.pipeline_versions_second_codes.count() > 0
    assert home.pipeline_versions_oldest_codes.count() > 0

    assert home.pipeline_versions_promote_latest_button.is_enabled()
    assert home.pipeline_versions_save_changes_button.is_enabled()

    # WHEN: The dialog is closed
    home.click_pipeline_versions_dialog_close_button()

    # THEN: The dialog is no longer visible
    assert not home.pipeline_versions_dialog.is_visible()
