from pages.base import Page
from regions.base import Region

from selenium.webdriver.common.by import By


class Home(Page):
    _create_new_job_button_locator = (By.CLASS_NAME, 'create-job-button')
    _pdf_job_form_modal_locator = (By.CLASS_NAME, 'job-modal')

    @property
    def loaded(self):
        return self.is_create_new_job_button_displayed


    @property
    def is_create_new_job_button_displayed(self):
        return self.is_element_displayed(*self._create_new_job_button_locator)

    @property
    def create_job_modal_is_open(self):
        return self.is_element_displayed(*self._pdf_job_form_modal_locator)

    def click_create_new_job_button(self):
        self.find_element(*self._create_new_job_button_locator).click()
        self.wait.until(lambda _: self.create_job_modal_is_open)
        return self.CreateJobModal(self, self.find_element(
            *self._pdf_job_form_modal_locator))

    class CreateJobModal(Region):
        _modal_cancel_button_locator = (By.CSS_SELECTOR, '.job-cancel-button > span')

        @property
        def cancel_button(self):
            return self.find_element(*self._modal_cancel_button_locator)

        def click_cancel_button(self):
            self.cancel_button.click()
            self.wait.until(lambda _: not self.page.create_job_modal_is_open)
