from tests.ui.pages.home import HomeCorgi
import pytest

from bs4 import BeautifulSoup


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-otto-book", "ottó-book", "main")],
)
def test_e2e_webview_jobs(chrome_page_slow, corgi_base_url, repo, book, version):
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

    # THEN: A new job is queued and verified
    if home.elapsed_time.inner_text() <= '00:00:03' and home.queued_job_type == "Web Preview (git)":

        while home.job_type_href is None:
            pass

        with chrome_page_slow.context.expect_page() as tab:
            home.click_job_type_icon()

        new_tab_title = tab.value.title()
        new_tab_content = tab.value.content()
        new_tab_url = tab.value.url

        preview_base_url = new_tab_url.split('pages', 1)[0] + 'pages/'

        book_title_mod = book.replace("-", " ")

        assert book_title_mod in new_tab_title

        soup = BeautifulSoup(new_tab_content, 'html.parser')

        for clink in soup.find_all('a', class_='styled__ContentLink-sc-18yti3s-1'):
            webview_preview_pages = preview_base_url + clink['href']

            tab.value.goto(webview_preview_pages)

            new_tab_content = tab.value.content()
            sopa = BeautifulSoup(new_tab_content, 'html.parser')

            for m_content in sopa.find_all('div', id='main-content'):
                for p_tag in m_content.find_all('p'):
                    assert len(p_tag.text) > 0
