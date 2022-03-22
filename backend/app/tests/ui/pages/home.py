from pages.base import Page
from regions.base import Region

from selenium.webdriver.common.by import By

from time import sleep


# Page objects for playwright UI tests
class HomeCorgi:
    def __init__(self, page):
        self.page = page

    @property
    def create_new_job_button_is_visible(self):
        return self.page.wait_for_selector("text=create a new job")

    def click_create_new_job_button(self):
        self.create_new_job_button_is_visible.click()

    @property
    def create_job_modal_is_open(self):
        return self.page.locator("job-modal")

    @property
    def create_button_is_visible(self):
        return self.page.wait_for_selector("button.create-button-start-job")

    def click_create_button(self):
        self.create_button_is_visible.click()

    @property
    def modal_cancel_button_is_visible(self):
        return self.page.locator("button.job-cancel-button")

    def click_modal_cancel_button(self):
        self.modal_cancel_button_is_visible.click()

    @property
    def pdf_radio_button(self):
        return self.page.locator("div.v-radio.pdf-radio-button")

    def click_pdf_radio_button(self):
        self.pdf_radio_button.click()

    @property
    def web_preview_radio_button(self):
        return self.page.locator("div.v-radio.preview-radio-button")

    def click_web_preview_radio_button(self):
        self.web_preview_radio_button.click()

    @property
    def pdf_git_radio_button(self):
        return self.page.locator("div.v-radio.git-pdf-radio-button")

    def click_pdf_git_radio_button(self):
        self.pdf_git_radio_button.click()

    @property
    def web_preview_git_radio_button(self):
        return self.page.locator("div.v-radio.git-preview-radio-button")

    def click_web_preview_git_radio_button(self):
        self.web_preview_git_radio_button.click()

    @property
    def modal_hint_text(self):
        return self.page.locator(
            "div.v-dialog__content.v-dialog__content--active > div > div > div.v-card__text"
        )

    @property
    def collection_id_field_texts(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(1) > div > div > div.v-text-field__details"
        )

    @property
    def version_field_texts(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(2) > div > div > div.v-text-field__details"
        )

    @property
    def style_field_texts(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(3) > div > div > div.v-text-field__details"
        )

    @property
    def content_server_field_texts(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(4) > div > div > div.v-text-field__details"
        )

    @property
    def collection_id_field(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(1) > div > div > div.v-input__slot > div > label"
        )

    def fill_collection_id_field(self, value):
        self.collection_id_field.fill(value)

    @property
    def version_field(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(2) > div > div > div.v-input__slot > div > label"
        )

    def fill_version_field(self, value):
        self.version_field.fill(value)

    @property
    def style_field(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(3) > div > div > div.v-input__slot > div.v-select__slot > label"
        )

    @property
    def style_field_drop(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(3) > div > div > div.v-input__slot > div.v-select__slot"
        )

    def fill_style_field(self, value):
        self.style_field.fill(value)

    def click_style_field(self):
        self.style_field_drop.click()

    @property
    def style_field_dropdown(self):
        return self.page.locator("#list-item-209-0 > div > div")

    @property
    def server_field(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(4) > div > div > div.v-input__slot > div.v-select__slot > label"
        )

    def fill_server_field(self, value):
        self.server_field.fill(value)

    @property
    def content_server_locator(self):
        return self.page.locator(
            "div:nth-child(2) > div:nth-child(4) > div > div > div.v-input__slot > div.v-select__slot > label"
        )

    def click_content_server(self):
        self.content_server_locator.click()

    @property
    def content_server_dropdown(self):
        return self.page.locator("div.v-menu__content")

    def click_content_server_dropdown(self, value):
        self.content_server_dropdown.locator(f"text={value}").click()

    @property
    def status_message(self):
        return self.page.locator(
            "div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td:nth-child(9)"
        )


# Page objects for selenium UI tests - these can be removed once all tests are in playwright
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

        _modal_pdf_radio_button_locator = (By.CLASS_NAME, "pdf-radio-button")

        _modal_web_preview_radio_button_locator = (
            By.CLASS_NAME,
            "preview-radio-button",
        )

        _modal_pdfgit_radio_button_locator = (By.CLASS_NAME, "git-pdf-radio-button")

        _modal_git_preview_radio_button_locator = (
            By.CLASS_NAME,
            "git-preview-radio-button",
        )

        _modal_collection_id_field_locator = (
            By.CSS_SELECTOR,
            ".collection-id-field input",
        )

        _modal_version_field_locator = (
            By.CSS_SELECTOR,
            ".version-field input",
        )

        _modal_style_field_locator = (
            By.CSS_SELECTOR,
            ".style-field input",
        )

        _modal_server_field_locator = (
            By.CSS_SELECTOR,
            ".server-field input",
        )

        _modal_collection_id_field_error_locator = (
            By.CLASS_NAME,
            "collection-id-error-text",
        )

        _modal_collection_id_slug_field_error_locator = (
            By.CLASS_NAME,
            "collection-id-field",
        )

        _modal_collection_id_incorrect_field_error_locator = (
            By.CLASS_NAME,
            "collection-id-incorrect-error-text",
        )

        _modal_collection_id_slug_incorrect_field_error_locator = (
            By.CLASS_NAME,
            "collection-id-field",
        )

        _modal_style_field_error_locator = (By.CLASS_NAME, "style-error-text")

        _modal_content_server_field_error_locator = (By.CLASS_NAME, "server-error-text")

        _modal_status_message_locator = (
            By.XPATH,
            "//div[contains(@class,'jobs-table')]/div/table/tbody/tr[1]/td[9]/span/span/span",
        )

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
        def pdfgit_radio_button(self):
            return self.find_element(*self._modal_pdfgit_radio_button_locator)

        def click_pdfgit_radio_button(self):
            self.pdfgit_radio_button.click()

        @property
        def web_preview_radio_button(self):
            return self.find_element(*self._modal_web_preview_radio_button_locator)

        def click_web_preview_radio_button(self):
            self.web_preview_radio_button.click()

        @property
        def web_preview_git_radio_button(self):
            return self.find_element(*self._modal_pdfgit_radio_button_locator)

        def click_web_preview_git_radio_button(self):
            self.web_preview_git_radio_button.click()

        @property
        def collection_id_field_error(self):
            return self.find_element(*self._modal_collection_id_field_error_locator)

        @property
        def collection_id_slug_field_error(self):
            return self.find_element(
                *self._modal_collection_id_slug_field_error_locator
            )

        @property
        def collection_id_incorrect_field_error(self):
            return self.find_element(
                *self._modal_collection_id_incorrect_field_error_locator
            )

        @property
        def collection_id_slug_incorrect_field_error(self):
            return self.find_element(
                *self._modal_collection_id_slug_incorrect_field_error_locator
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

        @property
        def version_field(self):
            return self.find_element(*self._modal_version_field_locator)

        def fill_version_field(self, value):
            self.version_field.send_keys(value)

        @property
        def style_field(self):
            return self.find_element(*self._modal_style_field_locator)

        def fill_style_field(self, value):
            self.style_field.send_keys(value)

        @property
        def server_field(self):
            return self.find_element(*self._modal_server_field_locator)

        def fill_server_field(self, value):
            self.server_field.send_keys(value)

        @property
        def status_message(self):
            return self.find_element(*self._modal_status_message_locator)

        @property
        def is_pdf_radio_button_displayed(self):
            return self.is_element_displayed(*self._modal_pdf_radio_button_locator)

        @property
        def is_web_preview_radio_button_displayed(self):
            return self.is_element_displayed(
                *self._modal_web_preview_radio_button_locator
            )

        @property
        def is_pdfgit_radio_button_displayed(self):
            return self.is_element_displayed(*self._modal_pdfgit_radio_button_locator)

        @property
        def is_git_preview_radio_button_displayed(self):
            return self.is_element_displayed(
                *self._modal_git_preview_radio_button_locator
            )
