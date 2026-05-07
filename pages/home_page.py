from pages.base_page import BasePage

BASE_URL = "https://www.marksandspencer.in"

class HomePage(BasePage):

    def open(self):
        self.goto(BASE_URL)

    def search_product(self, product_name):

        search_box = self.page.locator(
            'input[placeholder*="Search"], input[type="search"]'
        ).first

        search_box.click()

        search_box.fill(product_name)

        search_box.press("Enter")

        self.page.wait_for_load_state("domcontentloaded")
