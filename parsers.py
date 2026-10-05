"""One function per competitor web shop: read one listing page, return (products, later pages).

A product is {listing_key, title, price, currency}. The later pages are the addresses of the listing
pages after this one, read from the page's pager, so the crawler can fetch them all at once. A new
competitor site needs a function here and an entry in PARSERS; config/client.yaml then names it
under `competitors` with its first pages.
"""

import re
from decimal import Decimal
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def price_of(text):
    return Decimal(re.sub(r"[^\d.]", "", text))


def books_toscrape(html, url):
    """books.toscrape.com (prices in GBP). Its pager says "Page 1 of 50"; pages are page-N.html."""
    soup = BeautifulSoup(html, "html.parser")
    products = [{
        "listing_key": urljoin(url, card.h3.a["href"]),
        "title": card.h3.a["title"],
        "price": price_of(card.select_one(".price_color").text),
        "currency": "GBP",
    } for card in soup.select("article.product_pod")]
    pager = re.search(r"Page (\d+) of (\d+)", soup.get_text())
    current, last = (int(pager[1]), int(pager[2])) if pager else (1, 1)
    return products, [urljoin(url, f"page-{n}.html") for n in range(current + 1, last + 1)]


def webscraper_io(html, url):
    """The webscraper.io test shop (prices in USD). Its pager links to ?page=N up to the last page."""
    soup = BeautifulSoup(html, "html.parser")
    products = []
    for card in soup.select("div.thumbnail"):
        name, specs = card.select_one("a.title")["title"], card.select_one(".description").text.strip()
        products.append({
            "listing_key": urljoin(url, card.select_one("a.title")["href"]),
            "title": specs if specs.startswith(name) else f"{name} {specs}",  # some specs repeat the name
            "price": price_of(card.select_one("[itemprop=price]").text),
            "currency": "USD",
        })
    numbers = [int(n) for a in soup.select("a.page-link[href]") for n in re.findall(r"[?&]page=(\d+)", a["href"])]
    current = int((re.findall(r"[?&]page=(\d+)", url) or ["1"])[0])
    return products, [urljoin(url, f"?page={n}") for n in range(current + 1, max(numbers, default=1) + 1)]


PARSERS = {"books_toscrape": books_toscrape, "webscraper_io": webscraper_io}
