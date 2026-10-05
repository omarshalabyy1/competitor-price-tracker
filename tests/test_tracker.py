"""Checks for the parts that break when a shop changes its pages or names: run with `pytest`."""

from decimal import Decimal
from pathlib import Path

import requests

import parsers
import tracker

PAGES = Path(__file__).parent / "pages"
THRESHOLD = 0.6  # the demo's rules.match_threshold; the tests never read a client's config


def test_books_page():
    url = "https://books.toscrape.com/catalogue/page-1.html"
    products, later_pages = parsers.books_toscrape((PAGES / "books-page-1.html").read_bytes(), url)
    assert len(products) == 20
    assert products[0] == {
        "listing_key": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "title": "A Light in the Attic",
        "price": Decimal("51.77"),
        "currency": "GBP",
    }
    assert len(later_pages) == 49  # "Page 1 of 50"
    assert later_pages[0] == "https://books.toscrape.com/catalogue/page-2.html"
    assert later_pages[-1] == "https://books.toscrape.com/catalogue/page-50.html"


def test_webscraper_page():
    url = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"
    products, later_pages = parsers.webscraper_io((PAGES / "webscraper-laptops-page-1.html").read_bytes(), url)
    assert len(products) == 6
    assert products[0]["title"] == 'Packard 255 G2 15.6", AMD E2-3800 1.3GHz, 4GB, 500GB, Windows 8.1'
    assert products[0]["price"] == Decimal("416.99")
    assert products[0]["listing_key"] == "https://webscraper.io/test-sites/e-commerce/static/product/31"
    assert len(later_pages) == 19  # the pager runs to page 20
    assert later_pages[0] == "https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page=2"
    assert later_pages[-1] == "https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page=20"


def test_last_page_has_no_later_pages():
    html = (PAGES / "books-page-1.html").read_text(encoding="utf-8").replace("Page 1 of 50", "Page 50 of 50")
    assert parsers.books_toscrape(html, "https://books.toscrape.com/catalogue/page-50.html")[1] == []


def test_same_product_named_differently_matches():
    assert tracker.similarity("Light in the Attic, A (Paperback)", "A Light in the Attic") == 1
    assert tracker.similarity("What If? (Paperback)", "What If?: Serious Scientific Answers") == 1
    assert tracker.similarity("One with You (Crossfire #5) (Paperback)", "One with You (Crossfire #5)") == 1
    assert tracker.similarity(
        "Lenovo V110-15ISK 128GB SSD Windows 10 Home 15.6 inch HD Core i3-6006U",
        'Lenovo V110-15ISK, 15.6" HD, Core i3-6006U, 4GB, 128GB SSD, Windows 10 Home',
    ) > THRESHOLD


def test_different_products_do_not_match():
    assert tracker.similarity("Tipping the Velvet", "A Light in the Attic") < THRESHOLD
    assert tracker.match_names({"vol-7": "Fruits Basket, Vol. 7 (Fruits Basket #7)"}, {"OURS-9": "Fruits Basket, Vol. 9"}, THRESHOLD) == []


def test_each_product_matches_one_listing_per_shop():
    titles = {"pro": 'Lenovo V110, 15.6", 4GB, 128GB SSD, Windows 10 Pro',
              "home": 'Lenovo V110, 15.6", 4GB, 128GB SSD, Windows 10 Home'}
    names = {"OURS-1": "Lenovo V110 15.6 inch 4GB 128GB SSD Windows 10 Home"}
    assert [(key, sku) for _, key, sku in tracker.match_names(titles, names, THRESHOLD)] == [("home", "OURS-1")]


def reply(status, headers=None):
    response = requests.Response()
    response.status_code, response.url = status, "https://shop.example/page"
    response.headers.update(headers or {})
    return response


def test_waits_out_a_rate_limit(monkeypatch):
    replies = [reply(429, {"Retry-After": "0"}), reply(503), reply(200)]
    monkeypatch.setattr(tracker.http, "get", lambda url, **kwargs: replies.pop(0))
    monkeypatch.setattr(tracker.time, "sleep", lambda seconds: None)
    assert tracker.get("https://shop.example/page").status_code == 200
    assert replies == []
