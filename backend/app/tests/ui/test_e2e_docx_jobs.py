import os

import pytest

from tests.ui.pages.home import HomeCorgi, JobStatus


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book",
    [("osbooks-otto-book", "hellas")],
)
def test_e2e_docx_jobs(chrome_page_slow, corgi_base_url, repo, book):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    current_job_id = home.next_job_id

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)

    home.click_docx_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and verified
    home.wait_for_job_created(current_job_id)
    home.wait_for_job_status(JobStatus.COMPLETED)

    if home.queued_job_type == "Docx (git)":
        with chrome_page_slow.expect_download() as download_info:
            home.click_job_type_icon()

        download = download_info.value

        assert "zip" in download.url

        assert repo and book in download.url

        download.save_as("docx.zip")

        assert os.path.getsize("docx.zip") > 0

    else:
        pytest.fail(
            "No new job was queued. Last job is at "
            + home.elapsed_time.inner_text()
        )
