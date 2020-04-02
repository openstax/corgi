from pages.base import Page
from regions.base import Region

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Home(Page):
    _create_new_pdf_button_locator = (
        By.CSS_SELECTOR, '#app > div > main > div > div > div > div > div.text-right > button > span')
    _pdf_job_form_modal_locator = (
        By.CSS_SELECTOR, '#app > div.v-dialog__content.v-dialog__content--active > div > div'
    )
    _previous_page_button_locator = (
        By.CSS_SELECTOR, '#app > div > main > div > div > div > div > div.d-md-flex > button:nth-child(1) > span'
    )
    _next_page_button_locator = (
        By.CSS_SELECTOR, '#app > div.v-application--wrap > main > div > div > div > div > div.d-md-flex > '
                         'button:nth-child(2) > span '
    )
    _go_button_locator = (
        By.CSS_SELECTOR,
        '#app > div.v-application--wrap > main > div > div > div > div > div.d-md-flex > button:nth-child(5) > span'
    )
    _page_field_locator = (
        By.CSS_SELECTOR,
        '#input-17'
    )
    _no_data_available = (By.CSS_SELECTOR, '# app > div > main > div > div > div > div > '
                                           'div.v-data-table.elevation-1.theme--light > div > table > tbody > tr > td')

    @property
    def loaded(self):
        return self.is_create_new_pdf_button_displayed

    @property
    def is_create_new_pdf_button_displayed(self):
        return self.is_element_displayed(*self._create_new_pdf_button_locator)

    @property
    def create_pdf_modal_is_open(self):
        return self.is_element_displayed(*self._pdf_job_form_modal_locator)

    @property
    def create_pdf_modal_is_closed(self):
        return self.is_element_displayed(*self._create_new_pdf_button_locator)

    def click_create_new_pdf_button(self):
        self.find_element(*self._create_new_pdf_button_locator).click()
        self.wait.until(lambda _: self.create_pdf_modal_is_open)
        return self.CreatePDFModal(self, self.find_element(*self._pdf_job_form_modal_locator))

    def click_previous_page_button(self):
        self.find_element(*self._previous_page_button_locator).click()
        return self

    def click_next_page_button(self):
        self.find_element(*self._next_page_button_locator).click()
        return self

    def click_go_button(self):
        self.find_element(*self._go_button_locator).click()
        return self

    @property
    def page_field(self):
        return self.find_element(*self._page_field_locator)

    def fill_in_page(self, value):
        self.page_field.send_keys(value)
        return self

    def no_data_available(self):
        return self.find_element(*self._no_data_available)

    class CreatePDFModal(Region):
        _modal_cancel_button_locator = (
            By.CSS_SELECTOR, '#app > div.v-dialog__content.v-dialog__content--active > div > div > '
                             'div.v-card__actions > button:nth-child(2) > span '
        )
        _modal_create_button_locator = (
            By.CSS_SELECTOR,
            '#app > div.v-dialog__content.v-dialog__content--active > div > div > div.v-card__actions > '
            'button:nth-child(3) > span '
        )

        def click_cancel_button(self):
            self.find_element(*self._modal_cancel_button_locator).click()
            return self

        def click_create_button(self):
            self.find_element(*self._modal_create_button_locator).click()
            return self

        def fill_collection_id_field(self, value):
            self.driver.find_element_by_tag_name("body").send_keys(Keys.TAB, value)
            return self

        def fill_version_field(self, value):
            self.driver.find_element_by_tag_name("body").send_keys(Keys.TAB, value)
            return self

        def fill_style_field(self, value):
            self.driver.find_element_by_tag_name("body").send_keys(Keys.TAB, value)
            return self

        def fill_server_field(self, value):
            self.driver.find_element_by_tag_name("body").send_keys(Keys.TAB, value)
            return self
