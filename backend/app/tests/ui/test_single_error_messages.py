import pytest
from pytest_testrail.plugin import pytestrail

from pages.home import HomeCorgi


@pytestrail.case("")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astro", "main")],
)
def test_single_same_error_message(chrome_page, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_docx_job_option()

    # WHEN: Create new job button is clicked
    home.click_create_new_job_button()

    # THEN: Error message dialog appears
    assert "Error: Book not in repository 'astro'" in home.error_message_dialog_locator.text_content()

    home.click_create_new_job_button()

    assert "Error: Book not in repository 'astro'" in home.error_message_dialog_locator.text_content()

    home.click_error_banner_okay_button()


@pytestrail.case("")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astron", "astronomy", "p888p")],
)
@pytest.mark.parametrize(
    "repo_2, book_2, version_2",
    [("osbooks-astronomy", "astronomy-2e", "")],
)
def test_single_non_dismissed_error_message(chrome_page, corgi_base_url, repo, book, version, repo_2, book_2, version_2):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_docx_job_option()
    home.click_pdf_job_option()
    home.click_webview_job_option()

    # WHEN: Create new job button is clicked
    home.click_create_new_job_button()

    # THEN: Error message dialog appears
    assert "Error: Could not resolve to a Repository with the name 'openstax/osbooks-astron'" in home.error_message_dialog_locator.text_content()

    home.fill_repo_field(repo_2)
    home.fill_book_field(book_2)
    home.fill_version_field(version_2)

    home.click_create_new_job_button()

    assert "Error: Could not resolve to a Repository with the name 'openstax/osbooks-astron'" in home.error_message_dialog_locator.text_content()

    home.click_error_banner_okay_button()

    assert not home.error_banner_is_visible


@pytestrail.case("")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astro", "main")],
)
def test_incorrect_book_corrected(chrome_page, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_webview_job_option()

    # WHEN: Create new job button is clicked
    home.click_create_new_job_button()

    # THEN: Error message dialog appears
    assert "Error: Book not in repository 'astro'" in home.error_message_dialog_locator.text_content()

    home.click_error_banner_okay_button()

    home.fill_book_field("astronomy-2e")

    home.click_create_new_job_button()

    assert not home.error_banner_is_visible


@pytestrail.case("")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astron", "astronomy-2e", "main")],
)
def test_incorrect_repo_corrected(chrome_page, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_docx_job_option()

    # WHEN: Create new job button is clicked
    home.click_create_new_job_button()

    # THEN: Error message dialog appears
    assert "Error: Could not resolve to a Repository with the name 'openstax/osbooks-astron'" in home.error_message_dialog_locator.text_content()

    home.click_error_banner_okay_button()

    home.fill_repo_field("osbooks-astronomy")

    home.click_create_new_job_button()

    assert not home.error_banner_is_visible


@pytestrail.case("")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astro", "p888p")],
)
def test_incorrect_version_corrected(chrome_page, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_docx_job_option()

    # WHEN: Create new job button is clicked
    home.click_create_new_job_button()

    # THEN: Error message dialog appears
    assert "Error: Could not find commit 'p888p'" in home.error_message_dialog_locator.text_content()

    home.click_error_banner_okay_button()

    home.fill_version_field(" ")

    home.click_create_new_job_button()

    assert not home.error_banner_is_visible


@pytestrail.case("C651216")
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("//osbooks-astronomy", "astronomy-2e", " ")],
)
def test_invalid_repo_error_message(chrome_page, corgi_base_url, repo, book, version):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_docx_job_option()

    # WHEN: Create new job button is clicked
    home.click_create_new_job_button()

    # THEN: Error message dialog appears
    assert "Error: Invalid repository" in home.error_message_dialog_locator.text_content()

    home.click_error_banner_okay_button()

    home.fill_repo_field("/osbooks-astronomy")
    home.click_version_field()
    home.click_webview_job_option()

    home.click_create_new_job_button()

    assert "Error: Could not resolve to a Repository with the name '/osbooks-astronomy'" in home.error_message_dialog_locator.text_content()

    home.click_error_banner_okay_button()

    home.fill_repo_field("osbooks-astronomy")
    home.click_version_field()
    home.click_pdf_job_option()

    home.click_create_new_job_button()

    assert not home.error_banner_is_visible
