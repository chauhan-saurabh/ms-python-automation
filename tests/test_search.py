from pages.home_page import HomePage

def test_search_product(page):

    home = HomePage(page)

    home.open()

    home.search_product("shirt")

    assert "search" in page.url.lower()
