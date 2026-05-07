# tests/test_cart.py

from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage


def test_add_product_to_cart(page):

    # -----------------------------------
    # HOME PAGE
    # -----------------------------------

    home = HomePage(page)

    home.open()

    page.wait_for_load_state("domcontentloaded")

    home.search_product("shirt")

    # Wait for product listing
    products = page.locator(
        '.product-grid a:visible[href*="/p/"], a:visible[href*="/p/"]'
    )

    expect(products.first).to_be_visible(timeout=20000)

    assert products.count() > 0

    print(f"PRODUCT COUNT => {products.count()}")

    # -----------------------------------
    # OPEN FIRST PRODUCT
    # -----------------------------------

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

    # Select Size
    size_selected = pdp.select_size()

    assert size_selected, "SIZE NOT SELECTED"

    print("SIZE SELECTED SUCCESSFULLY")

    # Select Type / Fit
    pdp.select_type()

    print("TYPE/FIT SELECTED SUCCESSFULLY")

    # Add to Bag
    pdp.add_to_bag()

    print("ADD TO BAG SUCCESSFULLY")

    # Verify Product Added
    pdp.verify_product_added_to_cart()

    print("PRODUCT ADDED TO CART SUCCESSFULLY")

    # -----------------------------------
    # CART PAGE
    # -----------------------------------

    cart = CartPage(page)

    cart.verify_cart_loaded()

    print("CART PAGE VERIFIED SUCCESSFULLY")

    # -----------------------------------
    # CHECKOUT FLOW
    # -----------------------------------

    cart.click_checkout()

    cart.verify_checkout_page()

    print("CHECKOUT LOGIN MODAL VERIFIED")

    # -----------------------------------
    # LOGIN FLOW
    # -----------------------------------

    cart.enter_mobile_number(
        "9997407473"
    )

    cart.click_continue_after_mobile()

    # Wait for password field
    password_field = page.locator(
        'input[type="password"]:visible'
    ).last

    expect(password_field).to_be_visible(
        timeout=20000
    )

    cart.enter_password(
        "Saw*9760320140"
    )

    cart.click_login_button()

    print("LOGIN BUTTON CLICKED")

    # -----------------------------------
    # VERIFY LOGIN SUCCESS
    # -----------------------------------

    cart.verify_login_success()

    print("LOGIN FLOW COMPLETED SUCCESSFULLY")