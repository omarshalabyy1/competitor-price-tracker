"""Run once, for the demo only: generate the made-up client's catalogue (data/input/catalogue.csv),
the products the tracker watches. The client competes with the stores in config/client.yaml:

- grocery: the 200 products sold in the most of those stores, at our own price near their usual price;
- books and devices: a sample of the web shops' products, named the way our catalogue names them
  (so the match step has real work to do), with the right answers kept in data/input/match_truth.csv.

A real client brings its own catalogue instead (data/input/README.md).

    python make_catalogue.py
"""

import csv
import random
import re
import statistics
from collections import defaultdict
from datetime import datetime, timezone

import tracker
from config import load_config
from parsers import PARSERS

random.seed(7)  # the same catalogue on every run
DATA = tracker.ROOT / "data" / "input"
SHOPS = {s["id"]: s for s in load_config()["competitors"]}


def our_price(price, below, above):
    """Our price: the competitor's price moved by -below to +above, ending in 9 cents."""
    return round(max(0.49, int(price * random.uniform(1 - below, 1 + above) * 10) / 10 + 0.09), 2)


def grocery_products():
    stores = [str(s["open_prices_location"]) for s in SHOPS.values() if "open_prices_location" in s]
    prices = tracker.fetch_open_prices(stores, datetime(2025, 9, 7, tzinfo=timezone.utc), datetime.now(timezone.utc))
    by_barcode = defaultdict(list)
    for p in prices:
        by_barcode[p["product_code"]].append(p)
    # The products the most stores sell, then the most reported: a fair stand-in for best sellers.
    ranked = sorted(by_barcode.items(), key=lambda kv: (-len({p["location_id"] for p in kv[1]}), -len(kv[1]), kv[0]))
    rows = []
    for i, (barcode, seen) in enumerate(ranked[:200], 1):
        product = seen[-1]["product"] or {}
        regular = [p["price"] for p in seen if not p["price_is_discounted"]] or [p["price"] for p in seen]
        tags = [t for t in product.get("categories_tags") or [] if t != "en:undefined"] or ["en:groceries"]
        rows.append({
            "sku": f"GRO-{i:04d}",
            "name": product.get("product_name") or f"Product {barcode}",
            "category": tags[0][3:].replace("-", " ").capitalize(),
            "barcode": barcode,
            "our_price": our_price(statistics.median(regular), 0.05, 0.10),
            "currency": "USD",
            "is_key": i <= 40,  # the 40 most widely sold are the key products
        })
    return rows


def our_book_name(title):
    """How our catalogue writes a book: subtitle sometimes dropped, article moved, format added."""
    name = re.split(r"[:(]", title)[0].strip() if random.random() < 0.3 else title
    article = re.match(r"(The|A|An) (.+)", name)
    if article and random.random() < 0.5:
        name = f"{article[2]}, {article[1]}"
    return f"{name} ({random.choice(['Paperback', 'Hardcover'])})" if random.random() < 0.6 else name


def our_device_name(title):
    """How our catalogue writes a device: model and screen first, then the specs in our own order,
    one of them left out."""
    first, *specs = title.replace('"', " inch").split(", ")
    if len(specs) > 1:
        specs.remove(random.choice(specs))
    random.shuffle(specs)
    return " ".join([first, *specs])


def web_shop_products():
    rows, truth = [], []

    books = tracker.crawl(SHOPS["books-toscrape"]["pages"][0], PARSERS["books_toscrape"])
    for i, book in enumerate(random.sample(books, 100), 1):
        rows.append({"sku": f"BOK-{i:04d}", "name": our_book_name(book["title"]), "category": "Books",
                     "barcode": "", "our_price": our_price(float(book["price"]), 0.07, 0.08),
                     "currency": "GBP", "is_key": random.random() < 0.2})
        truth.append({"sku": rows[-1]["sku"], "store_id": "books-toscrape", "listing_key": book["listing_key"]})

    devices = [{**d, "category": page.rsplit("/", 1)[1].replace("touch", "phones").capitalize()}
               for page in SHOPS["webscraper-io"]["pages"] for d in tracker.crawl(page, PARSERS["webscraper_io"])]
    for i, device in enumerate(random.sample(devices, 60), 1):
        rows.append({"sku": f"DEV-{i:04d}", "name": our_device_name(device["title"]), "category": device["category"],
                     "barcode": "", "our_price": our_price(float(device["price"]), 0.07, 0.08),
                     "currency": "USD", "is_key": random.random() < 0.2})
        truth.append({"sku": rows[-1]["sku"], "store_id": "webscraper-io", "listing_key": device["listing_key"]})
    return rows, truth


def write(file, rows):
    with open(DATA / file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{file}: {len(rows)} rows")


if __name__ == "__main__":
    shop_rows, truth = web_shop_products()
    write("catalogue.csv", grocery_products() + shop_rows)
    write("match_truth.csv", truth)
