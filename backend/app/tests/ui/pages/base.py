import pypom
from selenium.webdriver.common.by import By


class Page(pypom.Page):
    # Default to a 60 second timeout for CNX webview
    def __init__(self, driver, base_url=None, timeout=90, **url_kwargs):
        super().__init__(driver, base_url, timeout, **url_kwargs)

    @property
    def current_url(self):
        return self.driver.current_url
