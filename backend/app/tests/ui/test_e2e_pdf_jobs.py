from tests.ui.pages.home import HomeCorgi
import pytest

from urllib.request import urlopen, Request
from pypdf import PdfReader
import io


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-otto-book", "ottó-book", "main")],
)
def test_e2e_pdf_jobs(chrome_page_slow, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page_slow.goto(corgi_base_url)
    home = HomeCorgi(chrome_page_slow)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_pdf_job_option()

    # WHEN: The create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is queued and verified
    if home.elapsed_time.inner_text() <= '00:00:03' and home.queued_job_type == "PDF (git)":

        while home.check_href_attribute is None:
            pass

        with chrome_page_slow.context.expect_page() as tab:
            home.click_job_type_icon()

        new_tab_pdf = tab.value.url

        assert ".pdf" in new_tab_pdf

        r_url = Request(new_tab_pdf)
        pdf_url = urlopen(r_url).read()

        io_file = io.BytesIO(pdf_url)
        pdf_read = PdfReader(io_file)

        pdf_title = pdf_read.metadata.title

        book_adjusted = book.replace("-", " ")

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

                    liszt.append(ptext.split('\n'))

        flat_liszt = [item for sublist in liszt for item in sublist]

        try:
            assert any("CONTENT" in word for word in flat_liszt)
            assert any("Preface" in word for word in flat_liszt)
            assert any("Chapter Outline" in word for word in flat_liszt)
            assert any("Index" in word for word in flat_liszt)

        except AssertionError:
            pytest.fail(f"CONTENT, Preface, Chapter Outline or Index is missing in the pdf: {new_tab_pdf}")

        else:
            pass

    else:
        pytest.fail(f"No new job was queued. Last job is at {home.elapsed_time.inner_text()}")
