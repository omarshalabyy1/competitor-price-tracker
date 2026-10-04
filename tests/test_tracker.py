"""Checks for the parts that break when a shop changes its pages or names: run with `pytest`."""

from decimal import Decimal
from pathlib import Path

import tracker

PAGES = Path(__file__).parent / "pages"


def test_books_page():
    url = "https://books.toscrape.com/catalogue/page-1.html"
    products, next_page = tracker.parse_books((PAGES / "books-page-1.html").read_bytes(), url)
    assert len(products) == 20
    assert products[0] == {
        "listing_key": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "title": "A Light in the Attic",
        "price": Decimal("51.77"),
        "currency": "GBP",
    }
    assert next_page == "https://books.toscrape.com/catalogue/page-2.html"


def test_webscraper_page():
    url = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"
    products, next_page = tracker.parse_webscraper((PAGES / "webscraper-laptops-page-1.html").read_bytes(), url)
    assert len(products) == 6
    assert products[0]["title"] == 'Packard 255 G2 15.6", AMD E2-3800 1.3GHz, 4GB, 500GB, Windows 8.1'
    assert products[0]["price"] == Decimal("416.99")
    assert products[0]["listing_key"] == "https://webscraper.io/test-sites/e-commerce/static/product/31"
    assert next_page == "https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page=2"


def test_last_page_has_no_next():
    html = (PAGES / "books-page-1.html").read_text(encoding="utf-8").replace('<li class="next">', "<li>")
    assert tracker.parse_books(html, "https://books.toscrape.com/catalogue/page-50.html")[1] is None


def test_same_product_named_differently_matches():
    assert tracker.similarity("Light in the Attic, A (Paperback)", "A Light in the Attic") == 1
    assert tracker.similarity("What If? (Paperback)", "What If?: Serious Scientific Answers") == 1
    assert tracker.similarity("One with You (Crossfire #5) (Paperback)", "One with You (Crossfire #5)") == 1
    assert tracker.similarity(
        "Lenovo V110-15ISK 128GB SSD Windows 10 Home 15.6 inch HD Core i3-6006U",
        'Lenovo V110-15ISK, 15.6" HD, Core i3-6006U, 4GB, 128GB SSD, Windows 10 Home',
    ) > tracker.MATCH_THRESHOLD


def test_different_products_do_not_match():
    assert tracker.similarity("Tipping the Velvet", "A Light in the Attic") < tracker.MATCH_THRESHOLD
    assert tracker.match_names({"vol-7": "Fruits Basket, Vol. 7 (Fruits Basket #7)"}, {"OURS-9": "Fruits Basket, Vol. 9"}) == []


def test_each_product_matches_one_listing_per_shop():
    titles = {"pro": 'Lenovo V110, 15.6", 4GB, 128GB SSD, Windows 10 Pro',
              "home": 'Lenovo V110, 15.6", 4GB, 128GB SSD, Windows 10 Home'}
    names = {"OURS-1": "Lenovo V110 15.6 inch 4GB 128GB SSD Windows 10 Home"}
    assert [(key, sku) for _, key, sku in tracker.match_names(titles, names)] == [("home", "OURS-1")]
