# Input files

What the client supplies, as CSV with a header row, UTF-8. The file names are set in
`config/client.yaml` under `inputs`. Extra columns are ignored. `python tracker.py` (and the first
task of every Airflow run) stops with a one-line message if a file is missing or a required column
is not there, before the warehouse is touched.

## catalogue (`inputs.catalogue`)

Our products: one row per product we sell, with our own price. The tracker compares every
competitor price against these.

| Column | Type | Example |
|---|---|---|
| sku | text, unique | GRO-0001 |
| name | text: our name for the product, used to match web shop listings by name | Original Sichuan Chili Crisp |
| category | text, for the report's slicers | Condiments |
| barcode | text, empty if none; matches grocery listings exactly (keep the leading zeros) | 0860001697803 |
| our_price | decimal, above zero, in the competitors' currency | 11.59 |
| currency | text | USD |
| is_key | true or false: key products get the undercut alert | true |

A product with a barcode is matched to grocery store listings by barcode. A product without one is
matched to web shop listings by name: write the name as the product is commonly called (brand,
model, size), and the matcher pairs it with the closest competitor title above
`rules.match_threshold`.

## match_truth (`inputs.match_truth`, optional)

The right competitor listing for some of our web shop products, so the notebook can score the name
matching (right, wrong, missed). Leave the key empty, or the file out, and the notebook says the
matching was not scored.

| Column | Type | Example |
|---|---|---|
| sku | text, in catalogue | DEV-0001 |
| store_id | text, a competitor `id` in config/client.yaml | webscraper-io |
| listing_key | text: the listing's product page address | https://webscraper.io/test-sites/e-commerce/static/product/31 |

## Competitor stores (not a file: `competitors` in config/client.yaml)

Each competitor is one entry with `id`, `name`, `kind` and `city`, then either:

- **a web shop:** `parser` (a function in `parsers.py`) and `pages` (the first listing page or pages;
  the later pages are fetched in parallel). **A new site needs a new parser:** a function that
  reads one listing page and returns its products (page address, title, price, currency) and the
  addresses of the later listing pages, read from the page's pager, plus one saved page in
  `tests/pages/` and a test. That is the per-client work
  that cannot be done in advance.
- **a grocery store on Open Prices:** `open_prices_location`, the store's location id on
  prices.openfoodfacts.org. No code needed.

The demo files here were made by `make_catalogue.py` (360 products: 200 grocery, 100 books, 60
devices) and are shared under the Open Database License, as the README's Data section says.
