class Home:
    def __init__(self, page):
        self.page = page

    @property
    def create_new_job_button_locator(self):
        return self.page.wait_for_selector("text=create a new job")

    def click_create_new_job_button(self):
        self.create_new_job_button_locator.click()

    @property
    def create_button_locator(self):
        return self.page.wait_for_selector("button.create-button-start-job")
