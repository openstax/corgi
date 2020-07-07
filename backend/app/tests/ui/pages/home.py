from pages.base import Page
from regions.base import Region

from selenium.webdriver.common.by import By

from time import sleep


class Home(Page):
    _create_new_job_button_locator = (By.CLASS_NAME, "create-job-button")
    _pdf_job_form_modal_locator = (By.CLASS_NAME, "job-modal")

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
        return self.CreateJobModal(
            self, self.find_element(*self._pdf_job_form_modal_locator)
        )

    class CreateJobModal(Region):
        _modal_cancel_button_locator = (By.CLASS_NAME, "job-cancel-button")

        _modal_create_button_locator = (By.CLASS_NAME, "create-button-start-job")

        _modal_collection_id_field_locator = (By.CLASS_NAME, "collection-id-field")

        _modal_collection_id_field_error_locator = (
            By.CLASS_NAME,
            "collection-id-error-text",
        )

        _modal_collection_id_incorrect_field_error_locator = (
            By.CLASS_NAME,
            "collection-id-incorrect-error-text",
        )

        _modal_style_field_error_locator = (By.CLASS_NAME, "style-error-text")

        _modal_content_server_field_error_locator = (By.CLASS_NAME, "server-error-text")

        @property
        def cancel_button(self):
            return self.find_element(*self._modal_cancel_button_locator)

        def click_cancel_button(self):
            self.cancel_button.click()
            self.wait.until(lambda _: not self.page.create_job_modal_is_open)

        @property
        def create_button(self):
            return self.find_element(*self._modal_create_button_locator)

        def click_create_button(self):
            self.create_button.click()
            self.wait.until(lambda _: self.page.create_job_modal_is_open)
            sleep(2)

        @property
        def collection_id_field_error(self):
            return self.find_element(*self._modal_collection_id_field_error_locator)

        @property
        def collection_id_incorrect_field_error(self):
            return self.find_element(
                *self._modal_collection_id_incorrect_field_error_locator
            )

        @property
        def style_field_error(self):
            return self.find_element(*self._modal_style_field_error_locator)

        @property
        def content_server_field_error(self):
            return self.find_element(*self._modal_content_server_field_error_locator)

        @property
        def collection_id_field(self):
            return self.find_element(*self._modal_collection_id_field_locator)

        def fill_collection_id_field(self, value):
            self.collection_id_field.send_keys(value)
