import pytest

from pages.corgi.home import Home


@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_new_job_button(chrome_page, corgi_base_url):

    chrome_page.goto(corgi_base_url)

    new_job = Home(chrome_page)
    new_job.click_create_new_job_button()

    assert new_job.create_button_locator

    chrome_page.close()
