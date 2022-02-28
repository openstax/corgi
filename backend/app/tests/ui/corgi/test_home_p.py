import pytest

from pages.corgi.home import Home


@pytest.mark.otto
@pytest.mark.nondestructive
def test_create_new_job_button(chrome_browser, chrome_page):

    chrome_page.set_default_timeout(999999)

    chrome_page.goto("https://corgi-staging.openstax.org/")

    new_job = Home(chrome_page)

    new_job.click_create_new_job_button()
