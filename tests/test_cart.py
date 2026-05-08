# tests/test_cart.py
import os

from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage


def test_add_product_to_cart(page, steps):

    # -----------------------------------
    # HOME PAGE
    # -----------------------------------

    steps.add("Open M&S homepage")
    home = HomePage(page)
    home.open()
    page.wait_for_load_state("domcontentloaded")

    steps.add("Search for 'shirt'")
    home.search_product("shirt")

    # Wait for product listing
    products = page.locator(
        '.product-grid a:visible[href*="/p/"], a:visible[href*="/p/"]'
    )

    expect(products.first).to_be_visible(timeout=20000)
    assert products.count() > 0
    print(f"PRODUCT COUNT => {products.count()}")

    steps.add(f"Product listing loaded — {products.count()} products found")

    # -----------------------------------
    # OPEN FIRST PRODUCT
    # -----------------------------------

    steps.add("Open first product (PDP)")
    first_product = products.first
    first_product.scroll_into_view_if_needed()
    first_product.click(force=True)
    page.wait_for_load_state("domcontentloaded")
    print(f"PDP URL => {page.url}")

    # -----------------------------------
    # PRODUCT DETAIL PAGE
    # -----------------------------------

    pdp = ProductPage(page)
    pdp.handle_popups()

    steps.add("Select size")
    size_selected = pdp.select_size()
    assert size_selected, "SIZE NOT SELECTED"
    print("SIZE SELECTED SUCCESSFULLY")

    steps.add("Select type / fit (Reg / Long)")
    pdp.select_type()
    print("TYPE/FIT SELECTED SUCCESSFULLY")

    steps.add("Click Add to bag")
    pdp.add_to_bag()
    print("ADD TO BAG SUCCESSFULLY")

    steps.add("Verify product added to cart")
    pdp.verify_product_added_to_cart()
    print("PRODUCT ADDED TO CART SUCCESSFULLY")

    # -----------------------------------
    # CART PAGE
    # -----------------------------------

    cart = CartPage(page)

    steps.add("Verify cart page loaded")
    cart.verify_cart_loaded()
    print("CART PAGE VERIFIED SUCCESSFULLY")

    # -----------------------------------
    # CHECKOUT FLOW
    # -----------------------------------

    steps.add("Click Checkout button")
    cart.click_checkout()

    steps.add("Verify login modal appeared")
    cart.verify_checkout_page()
    print("CHECKOUT LOGIN MODAL VERIFIED")

    # -----------------------------------
    # LOGIN FLOW
    # -----------------------------------

    mobile   = os.environ["MS_MOBILE"]
    password = os.environ["MS_PASSWORD"]

    steps.add("Enter mobile number")
    cart.enter_mobile_number(mobile)

    steps.add("Click Continue")
    cart.click_continue_after_mobile()

    steps.add("Wait for password field")
    password_field = page.locator(
        'input[type="password"]:visible'
    ).last
    expect(password_field).to_be_visible(timeout=20000)

    steps.add("Enter password")
    cart.enter_password(password)

    steps.add("Click Login / Start Shopping")
    cart.click_login_button()
    print("LOGIN BUTTON CLICKED")

    # -----------------------------------
    # VERIFY LOGIN SUCCESS
    # -----------------------------------

    steps.add("Verify login success")
    cart.verify_login_success()
    print("LOGIN FLOW COMPLETED SUCCESSFULLY")