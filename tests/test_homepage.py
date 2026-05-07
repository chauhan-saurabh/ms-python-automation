from pages.home_page import HomePage

def test_homepage_loads(page):

    home = HomePage(page)

    home.open()

    assert "Marks" in page.title()
