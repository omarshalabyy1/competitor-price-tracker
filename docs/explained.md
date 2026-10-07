# The project explained, from zero

This page explains the whole project in plain words: what it does, what every word means, where every number comes from, and how to talk about it in an interview. You do not need to know SQL, Airflow or Power BI to read it.

[← Back to the README](../README.md)

## 1. The project in one minute

A shop sells 360 products. Its competitors change their prices all the time: a cut here, a promotion there, a rise next week. The shop only finds out when someone checks a few competitor sites by hand, and nobody writes the old prices down.

So the owner cannot answer simple questions:

- Which competitor changed a price this week, and by how much?
- Did anyone cut one of our most important products below our price?
- Was that cut a one-week promotion, or the new normal?

This project answers them. Once a week, on its own, it collects competitor prices, pairs each competitor product with the shop's own product, adds every price to a history that is never overwritten, and emails the owner when a key product is cut below the shop's price. A Power BI report, built step by step from `powerbi/`, shows where the shop stands against each store.

Think of it like a notebook kept at the till: every week someone walks round the competitors, writes each price on a new line with the date, and never rubs anything out. A price change is just a line that differs from the line before it.

## 2. Words you will meet

| Word | What it means here |
|---|---|
| **Competitor, store** | Another shop selling the same products. The config lists 11: 9 grocery stores and 2 web shops. |
| **Our catalogue** | The shop's own products and prices, in `data/input/catalogue.csv`. 360 products: 200 grocery, 100 books, 60 devices. |
| **SKU** | Stock keeping unit: the shop's own code for a product, like `GRO-0011`. |
| **Barcode** | The number under the stripes on a pack, like `0810063343064`. Kept as text so the leading zero stays. |
| **Key product** | A product the shop cares most about. Only key products get the alert email. 76 of the 360 are key. |
| **Listing** | One product as one competitor sells it: its page address (web shops) or its barcode (grocery stores), and its title. |
| **Price observation** | One price seen once: which listing, which day, what price. One row in the history. |
| **Shelf date** (`observed_on`) | The day the price was on the shelf or the page. |
| **Published** (`published_at`) | When the price could first be read. A shopper may publish a receipt days after the shopping trip. |
| **Run week** | The week a weekly run covers. It is named by its first day, a Sunday, like "the week of 2026-08-02". |
| **Caught week** | The first weekly run that had both the old and the new price, so the first run that could see a change. |
| **Price change** | A day's price that differs from the listing's previous price. A **cut** goes down, a **rise** goes up. |
| **Undercut** | A competitor cuts a key product to a price below ours. This is what fires the alert. |
| **Promotion** | A price the source marks as discounted (`is_discounted`). |
| **Price gap** | How far a competitor's latest price is from ours, in percent. Negative means the competitor is cheaper. |
| **Scraping, crawling** | Reading prices off web pages with a program instead of by hand. Crawling means following a shop's page list to read every page. |
| **HTML** | HyperText Markup Language: the text a web page is made of. The program reads prices out of it. |
| **Parser** | A small function that reads one shop's page and returns its products. `parsers.py` has one per web shop. |
| **Pager** | The "Page 1 of 50" or "1 2 3 … next" links at the bottom of a listing page. The parser reads it to find the later pages. |
| **URL** | Uniform resource locator: a web address. A web shop listing is keyed by its product page URL. |
| **API** | Application programming interface: a web address a program asks for data, and gets clean data back instead of a page. The grocery prices come from one. |
| **Rate limit** | A site's way of saying "too many requests, slow down" (codes 429 and 503). The program waits as long as the site asks (its `Retry-After` header), then carries on. |
| **Matching** | Deciding which competitor listing is which of our products. By **barcode** when there is one (an exact match), by **name** when there is not. |
| **Similarity score** | For name matching: the share of words two names have in common, from 0 to 1 (the code calls it Jaccard). 1 means the same words. |
| **Match threshold** | 0.6, in `config/client.yaml`. A listing is our product only when the names share more than 0.6 of their words. |
| **Answer file** | `data/input/match_truth.csv`: the right listing for each of the 160 web shop products, so the notebook can score the name matching. |
| **Database** | A program that stores tables and answers questions about them. This project uses **PostgreSQL** (often "Postgres"). Here it is called the **warehouse**. |
| **SQL** | Structured Query Language: the language used to build tables and ask a database questions. `sql/schema.sql` is SQL. |
| **Table, row, column** | Like a spreadsheet sheet: each row is one thing (one price), each column one fact about it (its date, its amount). |
| **View** | A saved question that looks like a table. It holds no data of its own: it is worked out from the tables each time it is read. |
| **Append-only** | Rows are only added, never changed or deleted. The price history works this way. |
| **Window function** | SQL that looks at the rows around a row. `lag()` fetches the previous price of the same listing, so a change can be found without storing it. |
| **Primary key (PK)** | The column or columns that make each row unique. A price is unique by store, listing, shelf date and source. |
| **Foreign key (FK)** | A column that must point to an existing row in another table, like a price pointing to its listing. |
| **Airflow** | A scheduler: it runs the steps in order, on a timetable, and retries a step that fails. |
| **DAG** | Directed acyclic graph: Airflow's name for a pipeline, a set of steps with arrows saying which runs after which. Here `competitor_prices`. |
| **Task** | One step in the DAG, like `match` or `send_alert`. |
| **Cron, UTC** | Cron is a short code for a timetable: `0 0 * * 0` means midnight every Sunday. UTC is Coordinated Universal Time, the clock it runs on. |
| **Catch-up** | When Airflow is first switched on, it runs every week since the start date, one after another, as if it had been running all along. |
| **Latest only** | A rule in the DAG: the web shops are read and the email is sent only on the newest week, not on the older weeks of the catch-up. |
| **Docker, Docker Compose** | Docker runs programs in ready-made boxes (containers), so nobody installs PostgreSQL or Airflow by hand. `docker-compose.yml` says which boxes to start. |
| **Port 5440, port 8090** | The "door numbers": the warehouse listens on 5440, the Airflow screen on 8090. Each portfolio project uses its own numbers. |
| **`.env`** | A file for secrets: the database password and the Gmail login. Never committed; `.env.example` shows its shape. |
| **YAML** | "YAML Ain't Markup Language": a simple text format for settings. `config/client.yaml` holds every value a client would change. |
| **CSV** | Comma-separated values: a plain text table, one row per line. The catalogue and the answer file are CSV. |
| **SMTP, Gmail app password** | SMTP (Simple Mail Transfer Protocol) is how a program sends email. An app password is a separate Gmail password just for this program. |
| **USD, GBP** | US dollars and British pounds. Grocery and device prices are in USD; the book shop's prices, and our book prices, are in GBP. |
| **Median** | The middle value when all values are sorted. Half are below it, half above. |
| **Python, pandas** | Python is a programming language. pandas is its library for tables. `tracker.py` and the notebook are Python. |
| **Notebook** | `analysis/analysis.ipynb`, a file that mixes code, its output and notes. It computes every number in the README. |
| **Power BI, Power Query, DAX** | Power BI is Microsoft's report tool. Power Query loads and shapes the data. DAX (Data Analysis Expressions) is its formula language for measures. |
| **Star schema** | One or more fact tables (here: daily prices, changes, gaps) in the middle, with lookup tables (product, store, date) around them. See [data-model.svg](data-model.svg). |
| **PNG, SVG** | Two image formats. PNG (Portable Network Graphics) is a picture made of pixels: the charts. SVG (Scalable Vector Graphics) is drawn from shapes and text: the diagrams. |

## 3. How it works, file by file

Run in this order (the commands are in the README's "Run it" section). Every weekly run does steps 1 to 4 in Airflow.

| Step | File | What it does |
|---|---|---|
| 0 | `docker-compose.yml`, `Dockerfile`, `sql/airflow-db.sql` | Starts the warehouse (port 5440) and Airflow (port 8090). Airflow keeps its own records in a second database. |
| 0 | `config/client.yaml`, `config.py`, `.env` | Hold every setting: competitors, thresholds, schedule, colours. `config.py` reads them and stops with a one-line message if one is missing. |
| 0 | `make_catalogue.py` | Run once, before everything else, to make the demo catalogue and the answer file. A real client brings its own catalogue instead. |
| 1 | `load_reference` in `tracker.py` + `sql/schema.sql` | Checks the catalogue file and its columns, creates the tables and views, and loads our 360 products and the 11 stores. Running it again updates them, it never duplicates them. |
| 2a | `collect_open_prices` in `tracker.py` | Asks the grocery price feed for every price published at the 9 grocery stores during the run's week, 100 per page, and adds them to the history. |
| 2b | `collect_web_shops` in `tracker.py` + `parsers.py` | Newest week only. Reads each web shop's first listing page, finds the later pages from its pager, reads them 8 at a time, and adds today's prices to the history. |
| 3 | `match` in `tracker.py` | Pairs grocery listings with our products by barcode, and web shop listings by name (redone every run, so a better new listing can take a product from a weaker match). |
| 4 | `send_alert` in `tracker.py` | Newest week only. Reads the `undercut` view for this week. If there is any, it emails the list and records it in `alert_sent`. |
| - | views in `sql/schema.sql` | `daily_price` (one price per listing per day), `price_change` (every change, found with `lag()`), `price_gap` (latest price against ours), `undercut` (what the email lists). Worked out every time they are read. |
| - | `dags/competitor_prices.py` | The Airflow DAG: step 1, then 2a and 2b, then 3, then 4, every Sunday at midnight UTC since 7 September 2025. |
| 5 | `analysis/analysis.ipynb` | Reads the warehouse, prints every number in the README and draws the charts in `docs/`. |
| 6 | `theme.py`, `powerbi/` | `theme.py` writes the Power BI theme from the config's colours. `powerbi/` builds the report step by step, with the numbers each card must show (`06-checks.md`). |
| - | `tests/test_tracker.py` | Checks that the page readers still read two saved pages, that the name matching pairs the right products, and that a rate limit is waited out. |

### Matching by name, with an example

The web shops have no barcodes, and our catalogue names products its own way. This pair is pinned by a test in `tests/test_tracker.py`:

- Ours: `Lenovo V110-15ISK 128GB SSD Windows 10 Home 15.6 inch HD Core i3-6006U`
- The shop's: `Lenovo V110-15ISK, 15.6" HD, Core i3-6006U, 4GB, 128GB SSD, Windows 10 Home`

The matcher keeps only the words that identify a product: lower case, no subtitle after a colon, no brackets at the end, and no filler words ("a", "an", "the", "inch"). Ours gives 11 words; the shop's gives the same 11 plus "4gb", so 12 in all. 11 / 12 = 0.917, above the 0.6 threshold, so they match. The test only asserts "above 0.6"; the 0.917 is worked out here, not printed by the repo. Then the closest pairs are taken first, and each listing and each product can be used only once.

### One real product, from collected price to the alert email

The product is **Medium Roast** (`GRO-0011`), the one in the README's alert email.

1. **Our catalogue.** `GRO-0011`, barcode `0810063343064`, our price 11.49 USD, key product: yes (`make_catalogue.py` marks the 40 grocery products sold at the most stores as key).
2. **Collect.** The grocery feed returns a price of 10.99 USD at Smart & Final extra! with a shelf date of 30 July 2026. It goes into `price_observation` with the barcode as its listing key. Its previous price there was 11.99 (the shelf date of that older price is not printed anywhere in the repo).
3. **Match.** The listing key equals our product's barcode, so the listing gets `sku = GRO-0011` and a match score of 1.
4. **Find the change.** `daily_price` keeps one price per listing per day. `price_change` uses `lag()` to fetch the previous price: 11.99, then 10.99. They differ, so it is a change, a cut. Its `change_pct` is (10.99 − 11.99) / 11.99 = −8.3% (worked out here from the view's formula; the notebook does not print it).
5. **Caught week.** The run for the week starting 2 August 2026 was the first that had both prices. The shelf date, 30 July, is before that week: one of the two prices was published after it was on the shelf, and the history still puts it on 30 July.
6. **Undercut test.** Three things must be true: the product is key (yes), the new price is below the old one (10.99 < 11.99, yes), and the new price is below ours (10.99 < 11.49 × (1 − 0 / 100) = 11.49, yes). So it is an undercut. The 0 is `rules.undercut_pct`: a client can set 5 to hear only about cuts more than 5% below their price.
7. **Email.** `send_alert` finds this one undercut for the week of 2026-08-02 and sends "General store price alert: 1 key product undercut (week of 2026-08-02)", with the line `Medium Roast: Smart & Final extra! 11.99 -> 10.99 on 2026-07-30 (ours 11.49, -4%)`. The −4% is (10.99 − 11.49) / 11.49 = −4.35%, shown to the nearest whole percent. Then a row goes into `alert_sent`: week 2026-08-02, 1 undercut (notebook cell 9).

## 4. Every number, explained

The notebook ([`analysis/analysis.ipynb`](../analysis/analysis.ipynb)) prints these unless a row says otherwise. The cell numbers count from 0, the first cell.

### The headline and the results

| Number | What it means | How it is worked out | Where |
|---|---|---|---|
| **356 products** | Our products with at least one matched competitor listing that has a price. | Distinct products in `price_gap`: 200 grocery + 156 web shop. 4 of our 360 were never matched. | notebook cell 3 |
| **10 stores** | Competitor stores that sell at least one of our products. | Distinct stores in `price_gap`: 8 grocery stores and 2 web shops. | notebook cell 3 |
| **127 price changes** | Times a competitor price on one of our products differed from the price before it. | Rows in the `price_change` view. All 127 are at grocery stores. | notebook cell 5 |
| **52 cuts and 75 rises** | 52 changes went down, 75 went up. | New price below or above the old one. | notebook cells 5 and 15 |
| **61% to a promotion** | Of the 127 changes, the share whose new price is marked as discounted. | Share of changes with `is_discounted` true. | notebook cell 5 |
| **56 weekly runs** | The weeks the history covers. | Weeks from the start week, 7 September 2025, to the last run's week. 56 weeks of 7 days end on 4 October 2026 (that end date is worked out here, not printed). | notebook cell 9 |
| **Each change within one run (100%)** | Every change was caught by the first weekly run that had both prices. | For each change, the notebook works out which week the later of the two prices was published in, and compares it with the week that caught it: 127 of 127 agree. | notebook cell 7 |
| **Median 2.8 days, never more than 7** | How long after a price is published the weekly alert would go out. | From the later publish time to the end of that run's week, when the run fires. A price published just after a run waits a full week: 7.0 days. | notebook cell 7 |
| **17 undercuts in 6 of 56 runs** | Cuts that took a key product below our price, and how many weeks they fell in. | Rows in the `undercut` view, and their distinct caught weeks. | notebook cell 9 |
| **200 of 200 by barcode** | Every grocery product of ours was found at a competitor. | Grocery products whose barcode appears as a listing. | notebook cell 11 |
| **156 of 160 by name, 0 wrong** | Web shop products the name matching found, checked against the answer file. | 156 right, 0 wrong, 4 missed (the missed 4 are why 356 is not 360). | notebook cell 11 |
| **64% priced below ours** | Of all 824 competitor listings, the share whose latest price is below ours. | Share of `price_gap` rows with a negative gap. 63.8% before rounding (`powerbi/06-checks.md`, C3). | notebook cell 13 |
| **28% to 88%, and 1 of 1** | The same share, store by store, in the chart. | Lowest: the electronics web shop, 28.3% of 60. Highest with more than one listing: 87.8% of 41. The smallest store has 1 listing, and it is cheaper: 1 of 1. | notebook cell 13 |
| **9.98** (price-history chart) | One key product (Original Sichuan Chili Crisp) at one store: 10.48 for months, then a cut to 9.98, below our 11.59. | The notebook picks the undercut product with the longest history at that store (7 daily prices, 1 undercut) and draws it. It does not print the prices; 10.48, 9.98 and 11.59 are listed with their SQL in `powerbi/06-checks.md`, C14. | notebook cell 17; `06-checks.md` C14 |
| **11.99 → 10.99, ours 11.49** (email) | The one undercut in the week of 2 August 2026. | Row 16 of the undercut table. See the worked example above. | notebook cell 9 |
| **−4%** (email) | How far the new price is below ours. | (10.99 − 11.49) / 11.49 = −4.35%, rounded by `send_alert` in `tracker.py`. Not printed by the notebook. | `tracker.py` |
| **30 July 2026, week of 2 August 2026** | The new price's shelf date, and the run that caught it. | `observed_on` and `caught_week` of that undercut row. | notebook cell 9 |
| **8 at a time** | Web shop listing pages read at once. | `PARALLEL_PAGES = 8`, a setting. The same `get()` gives up after 8 tries on a rate limit, then Airflow retries the task (2 retries, 5 minutes apart). | `tracker.py`, DAG |
| **Ports 8090 and 5440** | Where Airflow and the warehouse listen on your laptop. | Settings. | `docker-compose.yml` |
| **Airflow 3.3, PostgreSQL 17, Python 3.10** | The versions the project runs on. | Set in the files. | `Dockerfile`, `docker-compose.yml` |
| **200 grocery, 160 web shop products; nine stores** (Data section) | The made-up catalogue: 200 grocery + 100 books + 60 devices = 360. Nine grocery stores in the config. | Rows of `catalogue.csv`; entries in `competitors`. | `data/input/catalogue.csv`, `config/client.yaml` |

Things that can look wrong but are not:

- **10 stores, but the config lists 11.** The eleventh grocery store sells none of our 200 grocery products, so it has no listing to compare. It is a real result of the matching.
- **356 products, not 360.** The name matching missed 4 web shop products (and matched none wrongly). A missed match is safer than a wrong one: a wrong one would compare our price with another product's.
- **No price changes at the web shops.** The two web shops are practice sites whose prices do not change (README, Data). All 127 changes are at grocery stores.
- **Shelf dates long before September 2025.** The Power BI date table starts on 19 July 2024. The feed is read by the day a price was published, and shoppers sometimes publish old receipts. The history files each price under its shelf date.
- **A price that was already below ours still counts as an undercut.** The chili crisp was at 10.48, already below our 11.59, then cut to 9.98. The rule is "a cut, to a price below ours", so a further cut alerts again.
- **The email says −4% but the change is −8.3%.** The email compares the new price with ours (11.49); the change compares it with the old price (11.99).
- **2.8 days, but the README says shoppers upload late.** The 2.8 days count from when a price was published. From the shelf date to the alert it is a median 5 days (cell 7), mostly the time shoppers take to upload.
- **64% here, 63.8% in the Power BI checks.** The same number, rounded differently.
- **The email for the week of 2 August 2026 was sent on 6 October 2026.** The `alert_sent` row in cell 9 shows that date. The catch-up loads older weeks without emailing, so this email went out after the catch-up. The repo does not record how that run was started.

### The diagrams

| Number | Where you see it | What it means |
|---|---|---|
| **356, 10 stores, 127 changes caught, 17 undercuts** | header.svg | The same numbers as the results table above. |
| **4.00 → 3.00, ours at 4.29** | header.svg | A real undercut: one store cut ice cream bars (`GRO-0002`) from 4.00 to 3.00 on 4 February 2026, below our 4.29, caught by the run for the week of 1 February 2026. Row 8 of the undercut table, notebook cell 9. |
| **01 to 05** | how-it-works.svg | The five steps: collect, match, store, alert, report. |
| **1 to 4, wk 1 to wk 7** | weekly-loop.svg | The four steps of each weekly run, and seven weeks of one product. The chart has no prices on it: it is a drawing of the idea. The real example is the price-history chart. |
| **9 stores, 2 shops** | data-flow.svg | The 9 grocery stores read from the price feed, and the 2 web shops read from their pages. |
| **360** | data-flow.svg, data-model.svg | Rows in `product`: our catalogue. |
| **11** | data-flow.svg, data-model.svg | Rows in `store`: every competitor in the config, including the one with none of our products. |
| **0** next to `alert_sent` | data-flow.svg | The diagram counts the tables after the runs up to 4 October 2026. The one email was recorded on 6 October 2026, so the notebook now shows 1 row. |
| **824** | data-flow.svg, data-model.svg | Rows in `price_gap`: one per matched listing, 668 grocery + 156 web shop (cell 3). |
| **127** | data-flow.svg, data-model.svg | Rows in `price_change`. |
| **17** | data-flow.svg | Rows in `undercut`. |
| **1,018 rows** | data-flow.svg, data-model.svg | Rows in `daily_price` for our products: one per listing per day with a price. From `powerbi/06-checks.md` C2, not the notebook. The diagram says plainly that `listing`, `price_observation` and the whole of `daily_price` were not counted. |
| **808 rows** | data-model.svg | Days in the Power BI date table: 19 July 2024 to 4 October 2026, the first and last shelf dates of our products' prices, one row per day. From `powerbi/06-checks.md` C2 and `powerbi/02-model.md`. |
| **1 and \*** | data-model.svg | "One to many": one product, store or day has many price rows. |

## 5. What the results mean for the business

- **Competitors are cheaper on most listings.** 64% of competitor listings are priced below ours: 68.9% at the grocery stores and 42.3% at the web shops (`powerbi/06-checks.md`, C5). The owner can see product by product where the shop is expensive, instead of guessing.
- **Most price moves are promotions.** 61% of the 127 changes went to a price marked as a promotion. Because the history keeps every price, the owner can tell a one-week promotion from a lasting cut by looking at what came next.
- **The alerts are rare, so they get read.** 17 undercuts fell in only 6 of 56 weeks. In the other 50 weeks no email was due. An alert that fires every week is soon ignored.
- **Every change is seen within a week of being published.** Every one of the 127 changes was caught by the first run that could see it, a median 2.8 days after the price was published.
- **The matching can be trusted.** 0 wrong matches out of 160 web shop products checked, and every grocery product found by barcode. A wrong match would compare our price with another product's, and the alert would lie.

## 6. Interview questions you can expect

**Explain the project in 30 seconds.**
A shop only found out about competitor price cuts by checking sites by hand, and kept no history. I built a weekly Airflow pipeline that collects competitor prices from web pages and a price feed, matches each listing to our product by barcode or by name, keeps every price in an append-only history in PostgreSQL, and emails the owner when a key product is cut below our price. It tracks 356 products at 10 stores. Over 56 weekly runs it caught 127 price changes, each by the first run that could see it, and 17 undercuts on key products.

**Why store every price instead of only the latest one?**
A change is two prices compared. With only the latest price you cannot tell a cut from a promotion that ended, and you cannot answer "what was it last month". So `price_observation` is append-only, and changes are found with `lag()` in a view, never stored. If the rule for a change changes, the view changes and the history stays as it was.

**How do you handle a price that arrives late?**
The history is ordered by the shelf date, not by the day the price arrived. A receipt published three weeks late still slots in at the right place. The run that catches the change is the later of the two prices' run weeks (`greatest(run_week, lag(run_week))`), which is why the notebook can prove each change was caught by the first run that could see it.

**What happens if a run is repeated?**
Nothing is duplicated. A price is unique by store, listing, shelf date and source id, and the insert says `ON CONFLICT DO NOTHING`. Products and stores are inserted, or updated if their key is already there. The alert record is keyed by week. So clearing and re-running a week gives the same tables.

**How does the catch-up work, and why are the web shops on the latest week only?**
`catchup=True` makes Airflow run every week since the start date, and `max_active_runs=1` keeps them in order, so each week sees exactly what the schedule would have seen. The web shop pages only show today's price, so reading them for a week last year would store today's price under an old week. `LatestOnlyOperator` skips them, and the email, on older weeks. `match` has `trigger_rule="none_failed"` so it still runs when the web shop step is skipped.

**How does name matching work, and how do you know it is right?**
Keep the words that identify a product, then score two names by the share of words they have in common. The closest pairs are taken first, one listing per product per store, and only above 0.6. To check it, `make_catalogue.py` kept the right answer for all 160 web shop products in an answer file; the notebook scores against it: 156 right, 0 wrong, 4 missed. I chose a threshold that misses a few rather than matches wrongly.

**Two shoppers report different prices for the same day. Which one counts?**
The lower one. `daily_price` keeps one price per listing per day, lowest first, because that is the price a customer could pay.

**Why is the undercut threshold set on the database?**
`load_reference` writes `rules.undercut_pct` from the config into a database setting, and the `price_change` view reads it. So the email, the notebook and Power BI all use the same rule. Nobody can set it differently in one tool.

**What happens when a site says "too many requests"?**
`get()` waits as long as the site's `Retry-After` header asks (or 1, 2, 4 … seconds), and tries again. After 8 tries it stops the task, and Airflow retries it twice, 5 minutes apart. There is no fixed pause between requests: the site's own answer sets the pace.

**What would change for a real client?**
Their catalogue in `data/input/`, their competitors and thresholds in `config/client.yaml`, and their Gmail login in `.env`. A grocery store on the feed needs only its location id. A new web shop needs a new parser function and a saved page for its test: that is the per-client work.

## 7. Limits, in plain words

- The two web shops are practice sites whose prices never change, so every change and every alert in the results comes from the grocery stores.
- Grocery prices exist only when shoppers publish them. A store with few uploads (one has a single listing of ours) gives a thin picture, and a change is only seen once someone publishes the new price.
- Web shop pages show today's price only, so their history starts the day the tracker is switched on. It cannot be filled in for past weeks.
- The shop is made up: its catalogue and its prices were generated near the competitors' usual prices. The competitor prices are real.
- Name matching compares every listing with every product. That is fine for 160 products; for tens of thousands it would need a way to compare only likely pairs first.
- The book shop prices are in GBP and compared with our GBP book prices. There is no currency conversion: a client's catalogue must use the competitors' currency.
- The Power BI report is written out step by step in `powerbi/`, but its screenshots are not in the repo yet.
