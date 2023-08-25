from tests.ui.pages.home import HomeCorgi, JobStatus
import pytest


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize("repo", ["osbooks-otto-book"])
def test_e2e_webview_jobs_book_optional(chrome_page_slow, corgi_base_url, repo):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    current_job_id = home.next_job_id

    # WHEN: Repo input field is filled and a job check box is selected
    home.fill_repo_field(repo)

    home.click_webview_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and verified
    home.wait_for_job_created(current_job_id)
    home.wait_for_job_status(JobStatus.COMPLETED)

    if home.queued_job_type == "Web Preview (git)":
        assert "all" in home.book_title_column.inner_text()

        home.click_job_id()

        assert home.job_id_dialog_is_visible

        chrome_page_slow.keyboard.press("Escape")

        assert not home.job_id_dialog_is_visible

        assert (
            home.book_title_column_tooltip.inner_text()
            == home.job_type_icon_job_links_are_visible.inner_text().replace(" ", "")
        )

        home.click_job_type_icon()

        assert home.job_id_dialog_is_visible

        home.click_job_id_dialog_close_button()

        assert not home.job_id_dialog_is_visible

        assert (
            home.book_title_column_tooltip.inner_text()
            == home.job_type_icon_job_links_are_visible.inner_text().replace(" ", "")
        )

    else:
        pytest.fail(
            f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}"
        )
