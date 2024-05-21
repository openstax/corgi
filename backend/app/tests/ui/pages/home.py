from enum import Enum
from time import sleep, time


class JobStatus(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    FAILED = "failed"
    COMPLETED = "completed"
    ABORTED = "aborted"


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
        return self.page.locator("#repo-input input")

    def fill_repo_field(self, value):
        self.repo_field_input_locator.fill(value)

    def click_repo_field(self):
        self.repo_field_input_locator.click()

    @property
    def book_field(self):
        return self.page.wait_for_selector("id=book-input")

    @property
    def book_field_input_locator(self):
        return self.page.locator("#book-input input")

    def fill_book_field(self, value):
        self.book_field_input_locator.fill(value)

    def click_book_field(self):
        self.book_field_input_locator.click()

    @property
    def version_field(self):
        return self.page.wait_for_selector("id=version-input")

    @property
    def version_field_input_locator(self):
        return self.page.locator("#version-input input")

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
        return self.page.wait_for_selector("tr:nth-child(1) > td:nth-child(1) > button")

    def click_job_id(self):
        self.job_id.click()

    def job_ids(self, i):
        return self.page.wait_for_selector(
            f"tr:nth-child({i + 1}) > td:nth-child(1) > button", timeout=60000
        )

    @property
    def job_id_dialog_is_visible(self):
        return self.page.is_visible("div.mdc-dialog__container")

    @property
    def job_id_dialog_title(self):
        return self.page.locator("div.mdc-dialog__header")

    @property
    def job_id_dialog_close_button(self):
        return self.page.locator("div > div.mdc-dialog__actions :text('close')")

    @property
    def job_id_dialog_close_button_is_visible(self):
        return self.page.is_visible("div > div.mdc-dialog__actions :text('close')")

    def click_job_id_dialog_close_button(self):
        self.job_id_dialog_close_button.click()

    @property
    def job_id_dialog_approve_button(self):
        return self.page.locator("id=approve-button")

    @property
    def job_id_dialog_approve_button_is_visible(self):
        return self.page.is_visible("id=approve-button")

    def click_job_id_dialog_approve_button(self):
        self.job_id_dialog_approve_button.click()

    @property
    def job_id_dialog_repeat_button(self):
        return self.page.locator("id=repeat-button")

    @property
    def job_id_dialog_repeat_button_is_visible(self):
        return self.page.is_visible("id=repeat-button")

    def click_job_id_dialog_repeat_button(self):
        self.job_id_dialog_repeat_button.click()

    @property
    def abort_button_locator(self):
        return self.page.wait_for_selector("id=abort-button")

    @property
    def abort_button_is_visible(self):
        return self.page.is_visible("id=abort-button")

    def click_abort_button(self):
        self.abort_button_locator.click()

    @property
    def job_id_artifact_link_is_visible(self):
        return self.page.is_visible("#build-artifacts-frame > ul > li > a")

    @property
    def job_id_artifact_link_locator(self):
        return self.page.locator("#build-artifacts-frame > ul > li > a")

    def click_job_id_artifact_link(self):
        self.job_id_artifact_link_locator.click()

    @property
    def job_id_link_href(self):
        return self.job_id_artifact_link_locator.get_attribute("href", timeout=690000)

    @property
    def job_id_dialog_error_message_is_visible(self):
        return self.page.is_visible("div > div.mdc-dialog__content")

    @property
    def job_id_dialog_error_message(self):
        return self.page.wait_for_selector("div > div.mdc-dialog__content")

    @property
    def latest_job_status(self):
        return self.page.locator("td:nth-child(6) > img >> nth=0").get_attribute(
            "alt", timeout=690000
        )

    @property
    def latest_job_status_for_aborted(self):
        return self.page.locator("td:nth-child(6) > img >> nth=0").get_attribute(
            "alt=aborted", timeout=690000
        )

    def click_job_id_for_aborted(self):
        _ = self.latest_job_status_for_aborted  # Make sure alt=aborted exists
        self.job_id.click()

    @property
    def get_link_button_is_visible(self):
        return self.page.is_visible(
            "div.mdc-dialog__actions > button :text('Get Link')"
        )

    @property
    def get_link_button_locator(self):
        return self.page.locator("div.mdc-dialog__actions > button :text('Get Link')")

    def click_get_link_button(self):
        self.get_link_button_locator.click()

    def job_statuses(self, i):
        return self.page.locator(f"td:nth-child(6) > img >> nth={i}").get_attribute(
            "alt", timeout=690000
        )

    @property
    def elapsed_time(self):
        return self.page.wait_for_selector(
            "td:nth-child(7) > span > div:nth-child(1) >> nth=0", timeout=690000
        )

    @property
    def queued_repo_name(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(3) > span")

    @property
    def queued_job_type(self):
        return self.page.locator(
            "tr:nth-child(1) > td:nth-child(2) > a > img"
        ).get_attribute("alt", timeout=690000)

    @property
    def job_type_icon(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(2)")

    def click_job_type_icon(self):
        _ = self.job_type_href  # Make sure href exists
        self.job_type_icon.click()

    @property
    def job_type_href(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(2) > a").get_attribute(
            "href", timeout=690000
        )

    @property
    def version_sha(self):
        return self.page.locator("tr:nth-child(1) > td:nth-child(5)")

    @property
    def next_job_id(self):
        return int(self.job_id.inner_text()) + 1

    def click_version_sha(self):
        self.version_sha.click()

    def wait_for(self, condition, timeout_seconds=10, interval_seconds=0.25):
        start_time = time()
        while time() - start_time < timeout_seconds:
            if condition():
                return True
            sleep(interval_seconds)
        raise Exception("Timeout")

    def wait_for_job_created(self, job_id, timeout_seconds=10):
        return self.wait_for(
            lambda: int(self.job_id.inner_text()) == job_id, timeout_seconds
        )

    def wait_for_job_status(self, target_status, timeout_seconds=60 * 30):
        def _wait_for_job_status():
            latest_status = self.latest_job_status
            if latest_status == target_status:
                return True
            # raise Exception if the job concluded in an unexpected way
            if latest_status in (
                JobStatus.FAILED,
                JobStatus.ABORTED,
                JobStatus.COMPLETED,
            ):
                raise Exception(f"Job unexpectedly {latest_status}")

        return self.wait_for(_wait_for_job_status, timeout_seconds, 1)

    @property
    def job_type_icon_job_link(self):
        return self.page.locator("#build-artifacts-frame > ul > li:nth-child(4) > a")

    @property
    def job_type_icon_job_links_are_visible(self):
        return self.page.locator("#build-artifacts-frame > ul")

    def click_job_type_icon_job_link(self):
        self.job_type_icon_job_link.click()

    @property
    def book_title_column(self):
        return self.page.locator("tbody > tr:nth-child(1) > td:nth-child(4) > span")

    @property
    def book_title_column_shown_tooltip(self):
        return self.page.locator("[class='mdc-tooltip mdc-tooltip--shown']")

    @property
    def worker_version(self):
        return self.page.locator(
            "div.mdc-data-table__table-container > table > tbody > tr:nth-child(1) > td.lg.mdc-data-table__cell"
        )

    @property
    def current_jobs_row(self):
        return self.page.locator(
            "mdc-data-table__table-container > table > tbody > tr:nth-child(1)"
        )

    @property
    def job_id_approve_frame_code_version_is_visible(self):
        return self.page.is_visible("id=selected-code-version")
