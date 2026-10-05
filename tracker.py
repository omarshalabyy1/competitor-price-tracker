"""The weekly steps Airflow runs: load the reference data, collect competitor prices, match them to
our products, and email an alert when a key product is undercut. Each step is one function, and
every client value comes from load_config().

    python tracker.py    # check config/client.yaml, .env and data/input/, then load them
"""

import csv
import os
import re
import smtplib
import time
from datetime import datetime, timezone
from email.message import EmailMessage

import psycopg
import requests
from psycopg import sql

from config import ROOT, load_config
from parsers import PARSERS

USER_AGENT = "competitor-price-tracker (+https://github.com/omarshalabyy1/competitor-price-tracker)"
OPEN_PRICES_API = "https://prices.openfoodfacts.org/api/v1/prices"
CATALOGUE_COLUMNS = ["sku", "name", "category", "barcode", "our_price", "currency", "is_key"]

http = requests.Session()
http.headers["User-Agent"] = USER_AGENT


def connect(cfg):
    w = cfg["warehouse"]
    return psycopg.connect(host=w["host"], port=w["port"], dbname=w["database"], user=w["user"], password=w["password"])


# --- Step 1: reference data ------------------------------------------------------------------

def read_catalogue(cfg):
    """Our products from data/input/, after checking the file and its columns."""
    path = cfg["input_dir"] / cfg["inputs"]["catalogue"]
    if not path.exists():
        raise SystemExit(f"missing input file data/input/{path.name} (inputs.catalogue in config/client.yaml)")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in CATALOGUE_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"data/input/{path.name} is missing column(s): {', '.join(missing)}")
        return [[row[c] or None for c in CATALOGUE_COLUMNS] for row in reader]


def store_rows(cfg):
    """The competitor stores from config/client.yaml, after checking each web shop has a parser."""
    rows = []
    for s in cfg["competitors"]:
        if "parser" in s and s["parser"] not in PARSERS:
            raise SystemExit(f"config/client.yaml competitor {s['id']}: no parser {s['parser']} in parsers.py")
        source, ref = ("web shop pages", s["pages"][0]) if "parser" in s else ("open prices", str(s["open_prices_location"]))
        rows.append([s["id"], s["name"], s["kind"], s["city"], source, ref])
    return rows


def load_reference():
    """Check the config and the input files, create the tables and views, then load our catalogue
    and the competitor stores. The undercut rule's threshold is set on the database, so every
    connection (the alert, the notebook, Power BI) reads the same value."""
    cfg = load_config()
    products, stores = read_catalogue(cfg), store_rows(cfg)
    with connect(cfg) as conn:
        conn.execute(sql.SQL("ALTER DATABASE {} SET client.undercut_pct = {}").format(
            sql.Identifier(cfg["warehouse"]["database"]), sql.Literal(str(cfg["rules"]["undercut_pct"]))))
        conn.execute((ROOT / "sql" / "schema.sql").read_text())
        for table, key, cols, rows in (
            ("store", "store_id", ["store_id", "name", "kind", "city", "source", "source_ref"], stores),
            ("product", "sku", CATALOGUE_COLUMNS, products),
        ):
            updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c != key)
            conn.cursor().executemany(
                f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))}) "
                f"ON CONFLICT ({key}) DO UPDATE SET {updates}",
                rows,
            )
            print(f"{table}: {len(rows)} rows loaded")


# --- Step 2a: grocery stores, from Open Prices ------------------------------------------------

def fetch_open_prices(location_ids, start, end):
    """Every product price published on Open Prices for these stores in [start, end)."""
    prices, page = [], 1
    while True:
        response = http.get(OPEN_PRICES_API, timeout=60, params={
            "location_id__in": ",".join(location_ids),
            "created__gte": start.isoformat(),
            "created__lte": end.isoformat(),
            "product_code__isnull": "false",
            "duplicate_of__isnull": "true",
            "order_by": "created",
            "size": 100,
            "page": page,
        })
        response.raise_for_status()
        body = response.json()
        prices += [p for p in body["items"] if parse_time(p["created"]) < end]
        if page >= body["pages"]:
            return prices
        page += 1
        time.sleep(1)  # one request a second keeps us well inside the API's limits


def collect_open_prices(start, end, run_week):
    """Load the week's grocery prices: every price published between start and end."""
    cfg = load_config()
    with connect(cfg) as conn:
        stores = dict(conn.execute("SELECT source_ref, store_id FROM store WHERE source = 'open prices'").fetchall())
        prices = fetch_open_prices(list(stores), start, end) if stores else []
        rows = [{
            "store_id": stores[str(p["location_id"])],
            "listing_key": p["product_code"],
            "title": (p["product"] or {}).get("product_name") or p["product_code"],
            "observed_on": p["date"],
            "price": p["price"],
            "currency": p["currency"],
            "is_discounted": bool(p["price_is_discounted"]),
            "source_id": str(p["id"]),
            "published_at": parse_time(p["created"]),
        } for p in prices]
        save(conn, rows, run_week)
        print(f"{len(rows)} grocery prices published from {start} to {end}")


def parse_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


# --- Step 2b: web shops, read page by page -----------------------------------------------------

def crawl(url, parse):
    """Follow a shop's listing pages from the first one. robots.txt is not read: the pace is the brake."""
    products = []
    while url:
        response = http.get(url, timeout=60)
        response.raise_for_status()
        page, url = parse(response.content, response.url)
        products += page
        time.sleep(2)  # never faster than one page every 2 seconds
    return products


def collect_web_shops(run_week):
    """Read every product price on the web shops' listing pages today."""
    cfg = load_config()
    now = datetime.now(timezone.utc)
    with connect(cfg) as conn:
        for shop in (s for s in cfg["competitors"] if "parser" in s):
            rows = [{**p, "store_id": shop["id"], "observed_on": now.date(), "is_discounted": False,
                     "source_id": "page", "published_at": now}
                    for first_page in shop["pages"] for p in crawl(first_page, PARSERS[shop["parser"]])]
            save(conn, rows, run_week)
            print(f"{shop['id']}: {len(rows)} prices read")


def save(conn, rows, run_week):
    """Keep each listing's latest title, and add each price to the history (never overwritten)."""
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO listing (store_id, listing_key, title) VALUES (%(store_id)s, %(listing_key)s, %(title)s) "
        "ON CONFLICT (store_id, listing_key) DO UPDATE SET title = EXCLUDED.title",
        rows,
    )
    cur.executemany(
        "INSERT INTO price_observation (store_id, listing_key, observed_on, price, currency, is_discounted,"
        " source_id, published_at, run_week) VALUES (%(store_id)s, %(listing_key)s, %(observed_on)s, %(price)s,"
        " %(currency)s, %(is_discounted)s, %(source_id)s, %(published_at)s, %(run_week)s) ON CONFLICT DO NOTHING",
        [{**r, "run_week": run_week} for r in rows],
    )


# --- Step 3: match competitor listings to our products -------------------------------------------

def words(name):
    """The words that identify a product: lower case, no subtitle, no series or format in brackets
    at the end, no filler."""
    main = re.sub(r"(\s*\([^)]*\))+\s*$", "", name.split(":")[0])
    return set(re.findall(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", main.lower())) - {"a", "an", "the", "inch"}


def similarity(a, b):
    """0 to 1: the share of words two product names have in common (Jaccard)."""
    a, b = words(a), words(b)
    return len(a & b) / len(a | b) if a | b else 0


def match_names(titles, names, threshold):
    """Pair a shop's listings {key: title} with our products {sku: name}, one to one, the most
    alike pairs first. Returns [(score, key, sku)] for the pairs above the threshold."""
    pairs = sorted(((similarity(title, name), key, sku) for key, title in titles.items()
                    for sku, name in names.items()), reverse=True)
    matched, used = [], set()
    for score, key, sku in pairs:
        if score <= threshold:
            break
        if key not in used and sku not in used:
            matched.append((score, key, sku))
            used |= {key, sku}
    return matched


def match():
    """Grocery listings match on barcode. Web shop listings match on product names, redone every
    run so a new listing can take a product from a weaker match."""
    cfg = load_config()
    with connect(cfg) as conn:
        by_barcode = conn.execute(
            "UPDATE listing l SET sku = p.sku, match_score = 1 FROM product p "
            "WHERE l.sku IS NULL AND p.barcode = l.listing_key"
        ).rowcount
        print(f"Grocery: {by_barcode} new listings matched by barcode")
        names = dict(conn.execute("SELECT sku, name FROM product WHERE barcode IS NULL").fetchall())
        for (store_id,) in conn.execute("SELECT store_id FROM store WHERE source = 'web shop pages'").fetchall():
            titles = dict(conn.execute("SELECT listing_key, title FROM listing WHERE store_id = %s", (store_id,)).fetchall())
            conn.execute("UPDATE listing SET sku = NULL, match_score = NULL WHERE store_id = %s", (store_id,))
            pairs = match_names(titles, names, cfg["rules"]["match_threshold"])
            for score, key, sku in pairs:
                conn.execute(
                    "UPDATE listing SET sku = %s, match_score = %s WHERE store_id = %s AND listing_key = %s",
                    (sku, round(score, 3), store_id, key),
                )
            print(f"{store_id}: {len(pairs)} of {len(titles)} listings matched by name")


# --- Step 4: alert ---------------------------------------------------------------------------------

def send_alert(run_week):
    """Email the key products a competitor cut below our price in this week's run."""
    cfg = load_config()
    with connect(cfg) as conn:
        rows = conn.execute(
            "SELECT store, product, observed_on, old_price, new_price, our_price FROM undercut "
            "WHERE caught_week = %s ORDER BY product, store",
            (run_week,),
        ).fetchall()
        if not rows:
            print("No key product undercut this week")
            return
        if not os.environ.get("GMAIL_APP_PASSWORD"):
            print(f"{len(rows)} undercuts, but GMAIL_USER and GMAIL_APP_PASSWORD are not set in .env: no email")
            return
        currency = cfg["client"]["currency"]
        message = EmailMessage()
        message["Subject"] = f"{cfg['client']['name']} price alert: {len(rows)} key products undercut (week of {run_week})"
        message["From"] = os.environ["GMAIL_USER"]
        message["To"] = cfg["alert"]["to"] or os.environ["GMAIL_USER"]
        message.set_content("\n".join(
            [f"Competitors cut these key products below our price (week of {run_week}, prices in {currency}):", ""]
            + [f"- {product}: {store} {old} -> {new} on {day} (ours {ours}, {(new - ours) / ours:+.0%})"
               for store, product, day, old, new, ours in rows]
        ))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"])
            smtp.send_message(message)
        conn.execute(
            "INSERT INTO alert_sent (run_week, sent_at, undercuts) VALUES (%s, now(), %s) "
            "ON CONFLICT (run_week) DO UPDATE SET sent_at = now(), undercuts = EXCLUDED.undercuts",
            (run_week, len(rows)),
        )
        print(f"Alert sent: {len(rows)} undercuts")


if __name__ == "__main__":
    load_reference()
