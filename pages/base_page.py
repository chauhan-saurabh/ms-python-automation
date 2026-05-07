class BasePage:

    def __init__(self, page):
        self.page = page

    def goto(self, url):
        self.page.goto(url, wait_until="domcontentloaded")

    def close_popups(self):

        try:
            accept_btn = self.page.locator(
                'button:has-text("Accept"), button:has-text("Allow")'
            ).first

            if accept_btn.is_visible():
                accept_btn.click()

        except:
            pass
