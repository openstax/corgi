class HomeCorgi:
    def __init__(self, page):
        self.page = page

    @property
    def book_input_fields(self):
        return self.page.locator("child(2) > div > div:nth-child(2)")

    @property
    def job_types_check_boxes(self):
        return self.page.locator("child(2) > div > div:nth-child(3)")

    @property
    def jobs_data_table(self):
        return self.page.locator("div.mdc-data-table")

    @property
    def jobs_pagination_box(self):
        return self.page.locator("div.mdc-data-table__pagination")

    @property
    def repo_field(self):
        return self.page.wait_for_selector("id=repo-input")

    @property
    def repo_field_input_locator(self):
        return self.page.locator('#repo-input input')

    def fill_repo_field(self, value):
        self.repo_field_input_locator.fill(value)

    def click_repo_field(self):
        self.repo_field_input_locator.click()

    @property
    def book_field(self):
        return self.page.wait_for_selector("id=book-input")

    @property
    def book_field_input_locator(self):
        return self.page.locator('#book-input input')

    def fill_book_field(self, value):
        self.book_field_input_locator.fill(value)

    def click_book_field(self):
        self.book_field_input_locator.click()

    @property
    def version_field(self):
        return self.page.wait_for_selector("id=version-input")

    @property
    def version_field_input_locator(self):
        return self.page.locator('#version-input input')

    def fill_version_field(self, value):
        self.version_field_input_locator.fill(value)

    def click_version_field(self):
        self.version_field_input_locator.click()

    @property
    def pdf_job_option(self):
        return self.page.wait_for_selector("id=PDF-job-option")

    def click_pdf_job_option(self):
        self.pdf_job_option.click()

    @property
    def webview_job_option(self):
        return self.page.wait_for_selector("id=Web-job-option")

    def click_webview_job_option(self):
        self.webview_job_option.click()

    @property
    def epub_job_option(self):
        return self.page.wait_for_selector("id=EPUB-job-option")

    def click_epub_job_option(self):
        self.epub_job_option.click()

    @property
    def docx_job_option(self):
        return self.page.wait_for_selector("id=Docx-job-option")

    def click_docx_job_option(self):
        self.docx_job_option.click()

    @property
    def create_new_job_button_is_enabled(self):
        return self.page.is_enabled("id=submit-job-button")

    @property
    def create_new_job_button_locator(self):
        return self.page.locator("id=submit-job-button")

    def click_create_new_job_button(self):
        self.create_new_job_button_locator.click()

    @property
    def error_message_dialog_locator(self):
        return self.page.locator("div.error.mdc-banner")

    @property
    def error_banner_okay_button_locator(self):
        return self.page.locator("div.error.mdc-banner :text('Okay')")

    def click_error_banner_okay_button(self):
        self.error_banner_okay_button_locator.click()

    @property
    def error_banner_is_visible(self):
        return self.page.is_visible("div.error.mdc-banner")

    @property
    def repo_dropdown_is_visible(self):
        return self.page.locator("#repo-input input")

    @property
    def book_dropdown_is_visible(self):
        return self.page.locator("#book-input input")

    @property
    def version_dropdown_is_visible(self):
        return self.page.locator("#version-input input")

    @property
    def job_id(self):
        return self.page.locator("td.mdc-data-table__cell--numeric >> nth=0")

    def click_job_id(self):
        self.job_id.click()

    @property
    def job_id_dialog_is_visible(self):
        return self.page.is_visible("div.mdc-dialog__container")

    @property
    def job_id_dialog_title(self):
        return self.page.locator("div.mdc-dialog__header")

    @property
    def job_id_dialog_close_button(self):
        return self.page.locator("div.mdc-dialog__actions > button:nth-child(2)")

    def click_job_id_dialog_close_button(self):
        self.job_id_dialog_close_button.click()

    @property
    def abort_button_locator(self):
        return self.page.wait_for_selector("id=abort-button")

    def click_abort_button(self):
        self.abort_button_locator.click()

    @property
    def job_id_pdf_link_is_visible(self):
        return self.page.is_visible("div.mdc-dialog__content > a")

    @property
    def job_id_pdf_link_locator(self):
        return self.page.locator("div.mdc-dialog__content > a")

    def click_job_id_pdf_link(self):
        self.job_id_pdf_link_locator.click()

    @property
    def job_id_link_href(self):
        return self.job_id_pdf_link_locator.get_attribute('href', timeout=690000)

    @property
    def latest_job_status(self):
        return self.page.locator("td:nth-child(6) > img >> nth=0").get_attribute('alt')

    @property
    def elapsed_time(self):
        return self.page.wait_for_selector("td:nth-child(7) >> nth=0", timeout=690000)

    @property
    def queued_repo_name(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(3)")

    @property
    def queued_job_type(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(2) > a > img").get_attribute('alt', timeout=690000)

    @property
    def job_type_icon(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(2)")

    def click_job_type_icon(self):
        _ = self.job_type_href  # Make sure href exists
        self.job_type_icon.click()

    @property
    def job_type_href(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(2) > a").get_attribute('href', timeout=690000)

    @property
    def version_sha(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(5)")

    def click_version_sha(self):
        self.version_sha.click()
