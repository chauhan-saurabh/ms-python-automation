# pages/product_page.py

from playwright.sync_api import Page, expect


class ProductPage:

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

    def safe_click(self, locator):

        locator.scroll_into_view_if_needed()

        expect(locator).to_be_visible()

        locator.click(force=True)

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
            'button[aria-label="close"]',

            '.close',
            '.close-btn',
            '.modal-close',
            '.popup-close'
        ]

        for selector in popup_selectors:

            try:

                elements = self.page.locator(selector)

                if elements.count() > 0:

                    for i in range(elements.count()):

                        element = elements.nth(i)

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
    # CHECK IF ELEMENT IS DISABLED
    # -----------------------------------

    def _is_disabled(self, element) -> bool:
        """
        Returns True if the element is disabled via:
        - the HTML disabled attribute/property
        - a CSS class containing 'disabled' or 'unavailable'
        """

        try:

            if element.is_disabled():
                return True

        except Exception:
            pass

        classes = (element.get_attribute("class") or "").lower()

        if "disabled" in classes or "unavailable" in classes:
            return True

        aria = (element.get_attribute("aria-disabled") or "").lower()

        if aria == "true":
            return True

        return False

    # -----------------------------------
    # SELECT SIZE
    # -----------------------------------

    def select_size(self):

        self.page.wait_for_load_state("domcontentloaded")

        self.page.screenshot(
            path="reports/before-size-selection.png",
            full_page=True
        )

        size_keywords = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

        possible_selectors = [
            'button',
            'label',
            'div[role="button"]',
            'span',
            '[class*="size"]',
            '[class*="Size"]',
            '[data-testid*="size"]'
        ]

        for selector in possible_selectors:

            try:

                elements = self.page.locator(selector)
                count = elements.count()

                print(f"CHECKING SELECTOR => {selector} => {count}")

                for i in range(count):

                    try:

                        item = elements.nth(i)

                        if not item.is_visible():
                            continue

                        text = item.inner_text().strip()

                        print(f"ELEMENT TEXT => {text}")

                        if text not in size_keywords:
                            continue

                        if self._is_disabled(item):
                            print(f"SIZE DISABLED => {text}, skipping")
                            continue

                        item.scroll_into_view_if_needed()
                        item.click(force=True)

                        print(f"SIZE SELECTED => {text}")

                        self.page.wait_for_timeout(800)

                        self.page.screenshot(
                            path="reports/after-size-selection.png",
                            full_page=True
                        )

                        print("SIZE SELECTED SUCCESSFULLY")
                        return True

                    except Exception as e:
                        print(f"SIZE ITEM FAILED => {e}")
                        continue

            except Exception as e:
                print(f"SELECTOR FAILED => {e}")
                continue

        self.page.screenshot(
            path="reports/size-not-found.png",
            full_page=True
        )

        print("NO SIZE FOUND")
        return False

    # -----------------------------------
    # SELECT TYPE / FIT
    # -----------------------------------

    def select_type(self):
        """
        Selects a Type/Fit option (e.g. Reg, Long, Slim).

        Strategy:
        1. Look for a label/heading with text 'Type' or 'Fit' to locate
           the correct section container.
        2. Within that container, find the first enabled option and click it.
        3. Fall back to a broader scan if no labelled section is found.
        """

        type_keywords = [
            "Reg",
            "Regular",
            "Long",
            "Slim",
            "Tailored",
            "Tall",
            "Short",
            "Petite"
        ]

        self.page.wait_for_timeout(500)

        # --- Strategy 1: find the Type/Fit section by its label heading ---

        section_label_selectors = [
            '[class*="size"] label:has-text("Type")',
            '[class*="size"] label:has-text("Fit")',
            '[class*="Size"] label:has-text("Type")',
            '[class*="Size"] label:has-text("Fit")',
            'label:has-text("Type")',
            'label:has-text("Fit")',
            'span:has-text("Type")',
            'span:has-text("Fit")'
        ]

        for label_sel in section_label_selectors:

            try:

                label_el = self.page.locator(label_sel).first

                if not label_el.is_visible(timeout=2000):
                    continue

                # Walk up to the section container (parent/grandparent)
                # then search for type options within it
                section = label_el.locator(
                    "xpath=ancestor::*[position()<=4]"
                ).last

                for keyword in type_keywords:

                    candidate = section.locator(
                        f'button:has-text("{keyword}"), '
                        f'span:has-text("{keyword}"), '
                        f'label:has-text("{keyword}")'
                    ).first

                    try:

                        if not candidate.is_visible(timeout=1000):
                            continue

                        if self._is_disabled(candidate):
                            print(f"TYPE DISABLED => {keyword}, skipping")
                            continue

                        candidate.scroll_into_view_if_needed()
                        candidate.click(force=True)

                        print(f"TYPE SELECTED => {keyword}")

                        self.page.wait_for_timeout(800)

                        print("TYPE/FIT SELECTED SUCCESSFULLY")
                        return True

                    except Exception:
                        continue

            except Exception:
                continue

        # --- Strategy 2: broad scan fallback ---

        print("SECTION LABEL NOT FOUND — trying broad scan")

        possible_selectors = [
            'button',
            'label',
            'div[role="button"]',
            'span'
        ]

        for selector in possible_selectors:

            try:

                elements = self.page.locator(selector)
                count = elements.count()

                for i in range(count):

                    try:

                        item = elements.nth(i)

                        if not item.is_visible():
                            continue

                        text = item.inner_text().strip()

                        if text not in type_keywords:
                            continue

                        if self._is_disabled(item):
                            print(f"TYPE DISABLED => {text}, skipping")
                            continue

                        item.scroll_into_view_if_needed()
                        item.click(force=True)

                        print(f"TYPE SELECTED => {text}")

                        self.page.wait_for_timeout(800)

                        print("TYPE/FIT SELECTED SUCCESSFULLY")
                        return True

                    except Exception:
                        continue

            except Exception:
                continue

        print("NO TYPE FOUND")
        return False

    # -----------------------------------
    # ADD TO BAG
    # -----------------------------------

    def add_to_bag(self):

        self.handle_popups()

        add_btn = self.page.locator(
            'button:has-text("Add to bag"), button:has-text("Add to Bag")'
        ).first

        expect(add_btn).to_be_visible(timeout=15000)

        # If still disabled after size+type, log the state for debugging
        if add_btn.is_disabled():

            self.page.screenshot(
                path="reports/failure_add_to_bag_disabled.png",
                full_page=True
            )

            raise AssertionError(
                "Add to bag is still disabled after size/type selection. "
                "Check reports/failure_add_to_bag_disabled.png — "
                "a required size dimension may not have been selected."
            )

        expect(add_btn).to_be_enabled(timeout=15000)

        add_btn.scroll_into_view_if_needed()

        self.page.screenshot(
            path="reports/before-add-to-bag.png",
            full_page=True
        )

        add_btn.click(force=True)

        print("ADD TO BAG CLICKED")

    # -----------------------------------
    # VERIFY PRODUCT ADDED TO CART
    # -----------------------------------

    def verify_product_added_to_cart(self):

        self.page.goto(
            "https://www.marksandspencer.in/cart",
            wait_until="domcontentloaded"
        )

        self.page.wait_for_load_state("domcontentloaded")

        self.page.wait_for_timeout(3000)

        self.page.screenshot(
            path="reports/cart-page.png",
            full_page=True
        )

        current_url = self.page.url

        print(f"CART URL => {current_url}")

        assert "cart" in current_url.lower()

        possible_cart_selectors = [

            '.product-info',
            '.cart-product',
            '.bag-item',
            '.item-details',
            '[data-cart-item]',
            '.mini-cart-products',
            '.product-name',
            '.line-item',
            '.product-line-item',

            # M&S specific
            'a[href*="/p/"]',
            '.product-card',
            '.cart-item'
        ]

        found = False

        for selector in possible_cart_selectors:

            try:

                locator = self.page.locator(selector)
                count = locator.count()

                print(f"{selector} => {count}")

                if count > 0:

                    if locator.first.is_visible(timeout=5000):

                        found = True

                        print(f"CART VERIFIED USING => {selector}")
                        break

            except Exception as e:

                print(f"FAILED SELECTOR => {selector} => {e}")
                continue

        assert found, "NO CART ITEM FOUND"

        print("PRODUCT ADDED TO CART SUCCESSFULLY")