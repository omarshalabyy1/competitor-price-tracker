"""One function per competitor web shop: read one listing page, return (products, next page URL).

A product is {listing_key, title, price, currency}. A new competitor site needs a function here and
an entry in PARSERS; config/client.yaml then names it under `competitors` with its first pages.
"""

import re
from decimal import Decimal
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def price_of(text):
    return Decimal(re.sub(r"[^\d.]", "", text))


def books_toscrape(html, url):
    """books.toscrape.com (prices in GBP)."""
    soup = BeautifulSoup(html, "html.parser")
    products = [{
        "listing_key": urljoin(url, card.h3.a["href"]),
        "title": card.h3.a["title"],
        "price": price_of(card.select_one(".price_color").text),
        "currency": "GBP",
    } for card in soup.select("article.product_pod")]
    next_link = soup.select_one("li.next a")
    return products, next_link and urljoin(url, next_link["href"])


def webscraper_io(html, url):
    """The webscraper.io test shop (prices in USD)."""
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
    next_link = soup.select_one("a[rel=next]")
    return products, next_link and urljoin(url, next_link["href"])


PARSERS = {"books_toscrape": books_toscrape, "webscraper_io": webscraper_io}
