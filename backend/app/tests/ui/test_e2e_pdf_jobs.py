import io
from urllib.request import Request, urlopen

import pytest
from pypdf import PdfReader

from tests.ui.pages.home import HomeCorgi, JobStatus


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-otto-book", "ottó-könyv", "main")],
)
def test_e2e_pdf_jobs(chrome_page_slow, corgi_base_url, repo, book, version):
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

    # THEN: A new job is queued and verified
    home.wait_for_job_created(current_job_id)
    home.wait_for_job_status(JobStatus.COMPLETED)

    if home.queued_job_type == "PDF (git)":
        if home.job_type_href:
            home.click_job_id()

        else:
            raise Exception("Missing URL in job_type_href element")

        if not home.job_id_dialog_is_visible:
            pytest.fail("Job ID dialog is not visible")

        else:
            while home.job_id_link_href is None:
                pass

            if not home.job_id_artifact_link_is_visible:
                pytest.fail("PDF link in Job ID dialog is not visible")
            else:
                home.click_job_id_artifact_link()

                href_pdf_url = home.job_id_link_href

                assert ".pdf" in href_pdf_url

                r_url = Request(href_pdf_url)
                pdf_url = urlopen(r_url).read()

                io_file = io.BytesIO(pdf_url)
                pdf_read = PdfReader(io_file)

                pdf_title = pdf_read.metadata.title

                book_adjusted = book.replace("-", " ")
                assert book_adjusted.lower() in pdf_title.lower()

                num_pages = len(pdf_read.pages)

                liszt = []

                if len(pdf_read.pages) < 1:
                    pytest.fail(f"No pages in pdf file: {repo}/{book}")

                else:
                    assert book_adjusted.lower() in pdf_title.lower()

                    for no in range(0, num_pages):
                        for ppage in pdf_read.pages:
                            ptext = ppage.extract_text()

                            try:
                                assert ptext is not None

                            except AssertionError:
                                pytest.fail(f"pdf page {no} is empty")

                            else:
                                pass

                            liszt.append(ptext.split("\n"))

                flat_liszt = [item for sublist in liszt for item in sublist]

                try:
                    assert any("Preface" in word for word in flat_liszt)
                    assert any("Chapter Outline" in word for word in flat_liszt)
                    assert any("Index" in word for word in flat_liszt)

                except AssertionError:
                    pytest.fail(
                        f"CONTENT, Preface, Chapter Outline or Index is missing in the pdf: {href_pdf_url}"
                    )

                else:
                    pass

    else:
        pytest.fail(
            f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}"
        )
