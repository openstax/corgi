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

    @property
    def job_state_locator(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(9)")

    @property
    def job_state_completed(self):
        return self.job_state_locator.locator("text=completed")

    @property
    def git_preview_link_locator(self):
        return self.page.locator(
            "div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td:nth-child(8) > ul > li:nth-child(2)"
        )

    @property
    def git_preview_link(self):
        return self.git_preview_link_locator.locator("text=View - Rex Web Prod")

    @property
    def git_view_locator(self):
        return self.page.locator(
            "div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td:nth-child(8)"
        )

    @property
    def git_view_link(self):
        return self.git_view_locator.locator("text=View")

    @property
    def pdf_view_locator(self):
        return self.page.locator(
            "div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td:nth-child(8)"
        )

    @property
    def pdf_view_link(self):
        return self.pdf_view_locator.locator("text=View")

    @property
    def start_date_time_locator(self):
        return self.page.locator(
            "div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td:nth-child(7)"
        )

    @property
    def start_date_time(self):
        return self.start_date_time_locator.locator("text=a few seconds ago")

    @property
    def job_id_locator(self):
        return self.page.locator(
            "div:nth-child(3) > div > div > table > tbody > tr:nth-child(1) > td:nth-child(7) > time"
        )
