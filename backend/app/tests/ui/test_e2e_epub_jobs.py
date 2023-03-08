from tests.ui.pages.home import HomeCorgi
import pytest

import os


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book",
    [("osbooks-astronomy", "astronomy-2e")],
)
def test_e2e_epub_jobs(chrome_page_slow, corgi_base_url, repo, book):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    latest_job_id = home.job_id.inner_text()

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)

    home.click_epub_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    current_job_id = home.job_id.inner_text()

    # THEN: A new job is queued and verified
    if int(current_job_id) == int(latest_job_id)+1 and home.queued_job_type == "EPUB (git)":

        with chrome_page_slow.expect_download() as download_info:
            home.click_job_type_icon()

        download = download_info.value

        assert "epub.zip" in download.url
        assert repo in download.url

        download.save_as("epub_doc.zip")

        assert os.path.getsize("epub_doc.zip") > 0

    else:
        pytest.fail(f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}")
