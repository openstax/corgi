import pytest

from pages.home import Home


@pytest.mark.ui
@pytest.mark.nondestructive
def test_create_new_pdf_button_is_displayed(selenium, base_url):
    # GIVEN: Selenium driver and the base_url

    # WHEN: The Home page is fully loaded
    home = Home(selenium, base_url).open()

    # THEN: The create new pdf button is displayed
    assert home.is_create_new_pdf_button_displayed
