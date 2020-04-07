from pages.base import Page
from regions.base import Region

from selenium.webdriver.common.by import By


class Home(Page):
    _create_new_pdf_button_locator = (
        By.CSS_SELECTOR, '#app > div > main > div > div > div > div > div.text-right > button')
    _pdf_job_form_modal_locator = (
        By.CSS_SELECTOR, '#app > div.v-dialog__content.v-dialog__content--active > div > div'
    )

    @property
    def loaded(self):
        return self.is_create_new_pdf_button_displayed

    @property
    def is_create_new_pdf_button_displayed(self):
        return self.is_element_displayed(*self._create_new_pdf_button_locator)

    @property
    def create_pdf_modal_is_open(self):
        return self.is_element_displayed(*self._pdf_job_form_modal_locator)

    def click_create_new_pdf_button(self):
        self.find_element(*self._create_new_pdf_button_locator).click()
        self.wait.until(lambda _: self.create_pdf_modal_is_open)
        return self.CreatePDFModal(self, self.find_element(*self._pdf_job_form_modal_locator))

    class CreatePDFModal(Region):
        _modal_cancel_button_locator = (
            By.CSS_SELECTOR, '#app > div.v-dialog__content.v-dialog__content--active > div > div > div.v-card__actions > button:nth-child(2) > span'
        )

        def click_cancel_button(self):
            self.find_element(*self._modal_cancel_button_locator).click()
            return self
