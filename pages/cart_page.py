# pages/cart_page.py

from playwright.sync_api import Page, expect


class CartPage:

    def __init__(self, page: Page):

        self.page = page

    # -----------------------------------
    # COMMON HELPERS
    # -----------------------------------

    def wait_for_visible(self, selector, timeout=15000):

        locator = self.page.locator(selector).first

        locator.wait_for(
            state="visible",
            timeout=timeout
        )

        return locator

    def safe_click(self, selector, timeout=15000):

        locator = self.wait_for_visible(
            selector,
            timeout
        )

        locator.scroll_into_view_if_needed()

        locator.click(force=True)

        print(f"CLICKED => {selector}")

    def safe_fill(self, selector, value, timeout=15000):

        locator = self.wait_for_visible(
            selector,
            timeout
        )

        locator.scroll_into_view_if_needed()

        locator.click(force=True)

        locator.clear()

        locator.type(
            value,
            delay=80
        )

        entered_value = locator.input_value()

        print(f"FILLED => {selector} => {entered_value}")

        assert entered_value != ""

    # -----------------------------------
    # HANDLE POPUPS
    # -----------------------------------

    def handle_popups(self):

        popup_selectors = [

            'button:has-text("Accept")',
            'button:has-text("Allow")',
            'button:has-text("I Agree")',
            'button:has-text("Got it")',

            '[aria-label="Close"]',

            '.close',
            '.close-btn',
            '.modal-close',
            '.popup-close'
        ]

        for selector in popup_selectors:

            try:

                locator = self.page.locator(selector)

                if locator.count() > 0:

                    for i in range(locator.count()):

                        element = locator.nth(i)

                        if element.is_visible():

                            try:

                                element.click(
                                    force=True,
                                    timeout=2000
                                )

                                print(
                                    f"POPUP CLOSED => {selector}"
                                )

                            except Exception:
                                continue

            except Exception:
                continue

    # -----------------------------------
    # VERIFY CART PAGE
    # -----------------------------------

    def verify_cart_loaded(self):

        self.page.wait_for_load_state(
            "domcontentloaded"
        )

        self.page.screenshot(
            path="reports/cart-loaded.png",
            full_page=True
        )

        current_url = self.page.url

        print(f"CART URL => {current_url}")

        assert "cart" in current_url.lower()

        selectors = [

            'h1:has-text("Cart")',
            'a:has-text("Checkout")',
            'button:has-text("Checkout")',
            'button:has-text("Proceed to Checkout")'
        ]

        found = False

        for selector in selectors:

            try:

                locator = self.page.locator(selector)

                if locator.count() > 0:

                    if locator.first.is_visible():

                        print(
                            f"CART VERIFIED => {selector}"
                        )

                        found = True

                        break

            except Exception:
                continue

        assert found, "Cart page not loaded"

        print("CART PAGE VERIFIED SUCCESSFULLY")

    # -----------------------------------
    # CLICK CHECKOUT
    # -----------------------------------

    def click_checkout(self):

        self.handle_popups()

        checkout_selectors = [

            'a:has-text("Checkout")',
            'button:has-text("Checkout")',
            'button:has-text("Proceed to Checkout")'
        ]

        clicked = False

        for selector in checkout_selectors:

            try:

                locator = self.page.locator(selector).first

                if locator.is_visible():

                    locator.scroll_into_view_if_needed()

                    locator.click(force=True)

                    print(
                        f"CHECKOUT CLICKED => {selector}"
                    )

                    clicked = True

                    break

            except Exception:
                continue

        assert clicked, "Checkout button not found"

    # -----------------------------------
    # VERIFY LOGIN MODAL
    # -----------------------------------

    def verify_checkout_page(self):

        modal_selectors = [

            'text=Login',
            '[role="dialog"]',
            '.modal',
            'input[type="text"]'
        ]

        found = False

        for selector in modal_selectors:

            try:

                locator = self.page.locator(selector)

                locator.first.wait_for(
                    state="visible",
                    timeout=15000
                )

                print(
                    f"LOGIN MODAL VERIFIED => {selector}"
                )

                found = True

                break

            except Exception:
                continue

        self.page.screenshot(
            path="reports/login-modal.png",
            full_page=True
        )

        assert found, "Login modal not opened"

        print("CHECKOUT FLOW VERIFIED SUCCESSFULLY")

    # -----------------------------------
    # ENTER MOBILE NUMBER
    # -----------------------------------

    def enter_mobile_number(self, mobile_number):

        # Wait for the login modal to fully render
        self.page.wait_for_timeout(3000)

        self.page.screenshot(
            path="reports/before-mobile-entry.png",
            full_page=True
        )

        # M&S uses a single username field that accepts mobile OR email.
        # Target it precisely by id/name before falling back to generic selectors.
        mobile_selectors = [
            '#login-form-username',
            'input[name="dwfrm_profile_customer_username"]',
            'input[type="tel"]',
            'input[name*="mobile"]',
            'input[name*="phone"]',
            'input[placeholder*="Mobile"]',
            'input[placeholder*="mobile"]',
            'input[placeholder*="Number"]',
        ]

        entered = False

        for selector in mobile_selectors:

            try:

                locator = self.page.locator(selector).first

                if not locator.is_visible(timeout=3000):
                    continue

                name        = locator.get_attribute("name")
                placeholder = locator.get_attribute("placeholder")
                input_type  = locator.get_attribute("type")

                print(
                    f"TRYING => {selector} | "
                    f"type={input_type}, name={name}, placeholder={placeholder}"
                )

                locator.scroll_into_view_if_needed()
                locator.click(force=True)
                locator.press("Meta+A")
                locator.press("Backspace")

                locator.type(mobile_number, delay=120)

                self.page.wait_for_timeout(500)

                value = locator.input_value()

                print(f"MOBILE ENTERED => {value}")

                if value == mobile_number:
                    entered = True
                    break

            except Exception as e:
                print(f"SELECTOR FAILED => {selector} => {e}")

        assert entered, "Mobile number not entered"

        print("MOBILE NUMBER ENTERED SUCCESSFULLY")

    # -----------------------------------
    # CLICK CONTINUE AFTER MOBILE
    # -----------------------------------

    def click_continue_after_mobile(self):

        buttons = self.page.locator('button:visible')
        count = buttons.count()
        clicked = False

        for i in range(count):

            try:

                button = buttons.nth(i)
                text = button.inner_text().strip()

                print(f"BUTTON => {text}")

                if text.lower() == "continue":

                    button.click(force=True)
                    clicked = True

                    print("CONTINUE CLICKED")
                    break

            except Exception:
                continue

        assert clicked, "Continue button not found"

        # After submitting a mobile number M&S India may show either:
        #   (a) a password field  — existing account
        #   (b) an OTP field      — new account or OTP-based login
        # Wait for whichever appears first.

        next_step_selectors = [
            'input[type="password"]:visible',
            'input[name*="password"]:visible',
            'input[placeholder*="Password"]:visible',
            'input[placeholder*="OTP"]:visible',
            'input[placeholder*="otp"]:visible',
            'input[name*="otp"]:visible',
            'input[placeholder*="One Time"]:visible',
        ]

        found_next = False

        for selector in next_step_selectors:

            try:

                locator = self.page.locator(selector).first

                locator.wait_for(
                    state="visible",
                    timeout=5000
                )

                print(f"NEXT STEP FIELD FOUND => {selector}")
                found_next = True
                break

            except Exception:
                continue

        if not found_next:

            self.page.screenshot(
                path="reports/after-continue-no-field.png",
                full_page=True
            )

            raise AssertionError(
                "Neither password nor OTP field appeared after clicking Continue. "
                "The mobile number may have been rejected — check "
                "reports/after-continue-no-field.png"
            )

    # -----------------------------------
    # ENTER PASSWORD
    # -----------------------------------

    def enter_password(self, password):

        password_selectors = [

            'input[type="password"]:visible',
            'input[name*="password"]:visible'
        ]

        entered = False

        for selector in password_selectors:

            try:

                locator = self.page.locator(selector).last

                locator.wait_for(
                    state="visible",
                    timeout=15000
                )

                locator.click(force=True)

                locator.clear()

                locator.type(
                    password,
                    delay=100
                )

                value = locator.input_value()

                print(f"PASSWORD VALUE => {value}")

                if value != "":

                    entered = True

                    break

            except Exception:
                continue

        assert entered, "Password field not found"

        print("PASSWORD ENTERED SUCCESSFULLY")

    # -----------------------------------
    # CLICK LOGIN BUTTON
    # -----------------------------------

    def click_login_button(self):

        buttons = self.page.locator(
            'button:visible'
        )

        count = buttons.count()

        clicked = False

        priority_buttons = [

            "Start Shopping",
            "START SHOPPING"
        ]

        # Exact match first
        for expected in priority_buttons:

            for i in range(count):

                try:

                    button = buttons.nth(i)

                    text = button.inner_text().strip()

                    print(f"BUTTON => {text}")

                    if text == expected:

                        button.click(force=True)

                        clicked = True

                        print(
                            f"CLICKED => {text}"
                        )

                        break

                except Exception:
                    continue

            if clicked:
                break

        # Fallback
        if not clicked:

            for i in range(count):

                try:

                    button = buttons.nth(i)

                    text = button.inner_text().strip()

                    if "shopping" in text.lower():

                        button.click(force=True)

                        clicked = True

                        print(
                            f"FALLBACK CLICKED => {text}"
                        )

                        break

                except Exception:
                    continue

        assert clicked, "Login button not found"

    # -----------------------------------
    # VERIFY LOGIN SUCCESS
    # -----------------------------------

    def verify_login_success(self):

        self.page.wait_for_load_state(
            "domcontentloaded"
        )

        self.page.screenshot(
            path="reports/login-success.png",
            full_page=True
        )

        success_selectors = [

            'text=Address',
            'text=Payment',
            'text=Deliver',
            'text=Logout',
            'text=My Account'
        ]

        found = False

        for selector in success_selectors:

            try:

                locator = self.page.locator(selector)

                if locator.count() > 0:

                    if locator.first.is_visible():

                        print(
                            f"LOGIN VERIFIED => {selector}"
                        )

                        found = True

                        break

            except Exception:
                continue

        assert found, "Login verification failed"

        print("LOGIN FLOW COMPLETED SUCCESSFULLY")