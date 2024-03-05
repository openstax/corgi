from pytest_testrail.plugin import pytestrail

from tests.ui.pages.home import HomeCorgi, JobStatus

import pytest


@pytestrail.case("C651147")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book",
    [("osbooks-otto-book", "ottó-könyv")],
)
def test_job_id_dialog_box_aborted_job(chrome_page_slow, corgi_base_url, repo, book):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    current_job_id = home.next_job_id

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)

    home.click_epub_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and job id dialog box buttons are verified
    home.wait_for_job_created(current_job_id)
    home.wait_for_job_status(JobStatus.QUEUED)

    home.click_job_id()

    assert home.abort_button_is_visible
    assert home.get_link_button_is_visible
    assert not home.job_id_dialog_repeat_button_is_visible
    assert not home.job_id_dialog_approve_button_is_visible
    assert not home.job_id_artifact_link_is_visible

    home.click_abort_button()

    assert not home.job_id_dialog_is_visible

    home.click_job_id_for_aborted()

    assert str(current_job_id) in home.job_id_dialog_title.inner_text()

    assert not home.abort_button_is_visible
    assert home.get_link_button_is_visible
    assert home.job_id_dialog_repeat_button_is_visible
    assert not home.job_id_dialog_approve_button_is_visible
    assert not home.job_id_artifact_link_is_visible

    home.click_job_id_dialog_close_button()


@pytestrail.case("C651147")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book",
    [("osbooks-otto-book", "tschüß-grüße")],
)
def test_job_id_dialog_box_completed_job(chrome_page_slow, corgi_base_url, repo, book):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    current_job_id = home.next_job_id

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)

    home.click_webview_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and job id dialog box buttons are verified
    home.wait_for_job_created(current_job_id)
    home.wait_for_job_status(JobStatus.COMPLETED)

    if home.queued_job_type == "Web Preview (git)":

        home.click_job_id()

        assert str(current_job_id) in home.job_id_dialog_title.inner_text()

        assert home.job_id_dialog_repeat_button_is_visible
        assert home.job_id_dialog_approve_button_is_visible
        assert home.job_id_artifact_link_is_visible
        assert not home.abort_button_is_visible
        assert home.get_link_button_is_visible

        home.click_get_link_button()

        assert not home.job_id_dialog_is_visible

    else:
        pytest.fail(f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}")


@pytestrail.case("C651147")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-failing-test-book", "failing-test-book", "main")],
)
def test_job_id_dialog_box_failed_job(chrome_page_slow, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    current_job_id = home.next_job_id

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_pdf_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and job id dialog box buttons are verified
    home.wait_for_job_created(current_job_id)
    home.wait_for_job_status(JobStatus.FAILED)

    if home.queued_job_type == "PDF (git)":
        home.click_job_id()

        assert str(current_job_id) in home.job_id_dialog_title.inner_text()

        assert home.job_id_dialog_repeat_button_is_visible
        assert not home.job_id_dialog_approve_button_is_visible
        assert not home.abort_button_is_visible
        assert not home.job_id_artifact_link_is_visible
        assert home.get_link_button_is_visible

        assert home.job_id_dialog_error_message_is_visible

        home.click_job_id_dialog_close_button()

        assert not home.job_id_dialog_is_visible

        home.click_job_id()
        assert home.job_id_dialog_error_message.inner_text() is not None
        assert not home.job_id_artifact_link_is_visible

        home.click_get_link_button()

        assert not home.job_id_dialog_is_visible

    else:
        pytest.fail(f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}")
