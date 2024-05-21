import pytest
from pytest_testrail.plugin import pytestrail

from tests.ui.pages.home import HomeCorgi


@pytestrail.case("C624696")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astro", "main")],
)
def test_incorrect_book_and_version_error_messages(
    chrome_page, corgi_base_url, repo, book, version
):
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

    # THEN: A new job is NOT queued and multiple error dialogs appear
    assert (
        "Error: Book not in repository 'astro'"
        in home.error_message_dialog_locator.text_content()
    )

    home.fill_version_field("p888p")

    home.click_create_new_job_button()

    assert (
        "Error: Book not in repository 'astro'"
        and "Error: Could not find commit 'p888p'"
        in home.error_message_dialog_locator.text_content()
    )

    home.click_error_banner_okay_button()


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astro", "main")],
)
def test_incorrect_repo_and_book_error_messages(
    chrome_page, corgi_base_url, repo, book, version
):
    # GIVEN: Playwright, chromium and the corgi_base_url

    # WHEN: The Home page is fully loaded
    chrome_page.goto(corgi_base_url)
    home = HomeCorgi(chrome_page)

    # WHEN: Input fields are filled and a job check box is selected
    home.fill_repo_field(repo)
    home.fill_book_field(book)
    home.fill_version_field(version)

    home.click_pdf_job_option()

    # WHEN: Create new job button is clicked
    home.click_create_new_job_button()

    # THEN: A new job is NOT queued and multiple error dialogs appear
    assert (
        "Error: Book not in repository 'astro'"
        in home.error_message_dialog_locator.text_content()
    )

    home.fill_repo_field("osbooks-astron")

    assert (
        "Error: Could not resolve to a Repository with the name 'openstax/osbooks-astron'"
        and "Error: Book not in repository 'astro'"
        in home.error_message_dialog_locator.text_content()
    )

    home.click_error_banner_okay_button()


@pytestrail.case("C624695")
@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astronomy-2e", "p888p")],
)
def test_incorrect_repo_and_version_error_messages(
    chrome_page, corgi_base_url, repo, book, version
):
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

    # THEN: A new job is NOT queued and multiple error dialogs appear
    assert (
        "Error: Could not find commit 'p888p'"
        in home.error_message_dialog_locator.text_content()
    )

    home.fill_repo_field("osbooks-astron")

    assert (
        "Error: Could not resolve to a Repository with the name 'openstax/osbooks-astron'"
        and "Error: Could not find commit 'p888p'"
        in home.error_message_dialog_locator.text_content()
    )

    home.click_error_banner_okay_button()


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astro", "main")],
)
def test_incorrect_repo_book_and_version_error_messages(
    chrome_page, corgi_base_url, repo, book, version
):
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

    # THEN: A new job is NOT queued and multiple error dialogs appear
    assert (
        "Error: Book not in repository 'astro'"
        in home.error_message_dialog_locator.text_content()
    )

    home.fill_version_field("p888p")
    home.fill_repo_field("osbooks-astron")

    assert (
        "Error: Could not resolve to a Repository with the name 'openstax/osbooks-astron'"
        and "Error: Book not in repository 'astro'"
        in home.error_message_dialog_locator.text_content()
    )

    home.click_error_banner_okay_button()


@pytest.mark.ui
@pytest.mark.nondestructive
@pytest.mark.parametrize(
    "repo, book, version",
    [("osbooks-astronomy", "astronomy-2e", "p888p")],
)
def test_incorrect_repo_and_version_error_messages_no_okay(
    chrome_page, corgi_base_url, repo, book, version
):
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

    # THEN: A new job is NOT queued and multiple error dialogs appear
    assert (
        "Error: Could not find commit 'p888p'"
        in home.error_message_dialog_locator.text_content()
    )

    home.fill_repo_field("osbooks-astron")
    home.click_version_field()

    assert (
        "Error: Could not resolve to a Repository with the name 'openstax/osbooks-astron'"
        and "Error: Could not find commit 'p888p'"
        in home.error_message_dialog_locator.text_content()
    )

    home.click_create_new_job_button()

    assert (
        "Error: Could not resolve to a Repository with the name 'openstax/osbooks-astron'"
        and "Error: Could not find commit 'p888p'"
        in home.error_message_dialog_locator.text_content()
    )

    home.click_error_banner_okay_button()
