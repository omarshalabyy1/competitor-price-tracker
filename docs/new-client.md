# New client

This repo is a GitHub template for the offering "Weekly competitor price tracking". A new client
gets a **private** repo from it (Use this template > Create a new repository > Private); client
data never goes into this public repo. Everything that changes per client is in `config/client.yaml`,
`.env` and `data/input/`, plus one function in `parsers.py` for each competitor web shop the template
does not read yet.

## Done in the template

What the client gets with no work. Hours are an estimate of building each part from scratch.

| Part | Estimate (hours) |
|---|---|
| Weekly Airflow pipeline in Docker: the warehouse, one run per week, the catch-up from a start week, the web shops read on the latest week only (`dags/`, `docker-compose.yml`, `Dockerfile`) | 4 |
| Grocery prices from Open Prices: any store there is a config line, no code (`tracker.py`) | 2 |
| Web shop reader: the first listing page, then every later page its pager lists, 8 at a time, as fast as the site answers, waiting out any "too many requests" reply (robots.txt is not read); two example parsers with saved pages and tests (`tracker.py`, `parsers.py`, `tests/`) | 3 |
| Matching: barcode for groceries, names for web shops on their identifying words, one listing per product per shop, closest pairs first (`tracker.py`, `tests/`) | 4 |
| Price history in SQL: every price kept, one price per listing per day, changes, gaps, undercuts with the client's threshold (`sql/schema.sql`) | 3 |
| The undercut email (`tracker.py`) | 1 |
| Client settings: `config/client.yaml`, `config.py` (`load_config()`), `.env`, the input check, the Power BI theme written from the config (`theme.py`) | 2 |
| Analysis notebook: every number, the "caught by the first possible run" check, the matching score, three charts (`analysis/analysis.ipynb`) | 4 |
| Power BI build pack: 6 queries, the model, 13 measures, 2 pages with 25 visuals, interactions, checks C1 to C15, a 37-step checklist (`powerbi/`) | 8 |
| README with its diagrams, and the input file guide (`data/input/README.md`) | 3 |
| **Total** | **34** |

## Configure

Per client, file by file. Hours are an estimate.

| File | Key | Example | Estimate (hours) |
|---|---|---|---|
| `config/client.yaml` | `client.name`, `client.currency`, `report.title`, `report.colours`, `alert.to` | `SEK`, `"#0F766E"` | 0.5 |
| `.env` | `DB_PASSWORD`, `GMAIL_USER`, `GMAIL_APP_PASSWORD` | a new password, a Gmail app password | 0.25 |
| `data/input/` catalogue | `inputs.catalogue` | `produkter.csv`: sku, name, barcode (leading zeros kept), our price, key products | 3 |
| `config/client.yaml` competitors on Open Prices | `competitors[].open_prices_location` | `942` | 0.5 |
| `config/client.yaml` rules, agreed with the client on a sample (an answer file in `inputs.match_truth` scores the matching) | `rules.match_threshold`, `rules.undercut_pct` | `0.7`, `10` | 1 |
| `config/client.yaml` schedule | `schedule.cron`, `schedule.timezone`, `schedule.start_date` | `"0 0 * * 1"`, `Europe/Stockholm`, `2026-08-03` | 0.25 |
| First run: the catch-up, `theme.py` and the notebook; fix what the checks report | | | 1 |
| Power BI: build from `powerbi/08-build-checklist.md` with the two parameters from `warehouse.*`; copy the notebook's numbers into `powerbi/06-checks.md` | `warehouse.*` | `127.0.0.1:5440`, `tracker` | 2 |
| **Total** | | | **8.5** |

## Custom

Typical work for one client beyond the template. Hours are an estimate.

| Work | Estimate (hours) |
|---|---|
| **A parser per competitor web shop the template does not read** (`parsers.py`): find the listing pages, the title and price parts of the page and how its pager names the later pages, save one page in `tests/pages/` with a test, run it on the live site. About 3 hours for a site whose pages carry their prices; add about 3 more for a site that builds its pages in the browser or sits behind a bot wall (a browser fetcher instead of plain requests). Typical client: three sites | 9 |
| Matching rules for the client's own naming beyond the default words (sizes, units, own brands) | 2 |
| Hosting the weekly run (a small server or the client's machine) and the Power BI refresh | 3 |
| **Total** | **14** |

The parser is the real per-client work: each competitor site is different, and a site that changes its
pages needs its parser updated (the saved page and the test show when).

## Share already done (estimate)

Template hours ÷ (template + configure + custom) hours = 34 ÷ (34 + 8.5 + 14) = 34 ÷ 56.5 = **60%**
(60.2%). With no new web shop to read (Open Prices stores only), custom drops to 5 hours and the share
to 34 ÷ 47.5 = 72%. Each extra site adds about 3 hours of custom work.

## Steps

1. Create the private repo from the template and clone it.
2. `cp .env.example .env` and set `DB_PASSWORD` (and the Gmail lines for the alert).
3. Edit `config/client.yaml`: client, competitors, rules, schedule, alert, colours.
4. Put the catalogue in `data/input/` ([columns and an example](../data/input/README.md)) and run
   `python tracker.py` to check it.
5. For each competitor web shop the template does not read: add its parser to `parsers.py` and a test.
6. `docker compose up -d --build`, switch `competitor_prices` on in Airflow and let it catch up; then
   `python theme.py` and run the notebook.
7. Build the Power BI report from `powerbi/`.

## Second-client drill (2026-10-05)

The acceptance test of the template: a fresh clone, a made-up second client, a run from scratch, and
every number checked against a hand calculation from the raw prices.

**Client B (drill):** Landskrona Livs, a grocer in Sweden. Currency `SEK`; time zone
`Europe/Stockholm`; runs on Mondays (`"0 0 * * 1"`) from `2026-08-03`; `match_threshold: 0.7`,
`undercut_pct: 10`; teal colours (`#0F766E` main), title "Landskrona Livs prices". Competitors: two
Landskrona stores on Open Prices (Willys, Maxi ICA) and one of the demo's web shops (the laptops pages
only). Catalogue: 20 rows in `produkter.csv` with an extra `supplier` column; 15 groceries in SEK, 5
laptops in USD named the client's way; no answer file. Cases on purpose: a key product cut more than
10% below our price (undercut), a key product cut below our price by less than 10% (not an undercut),
the same cut on a product that is not key (not an undercut), a laptop whose name scores 0.64 (missed
at 0.7), a laptop the shop does not sell.

| What | Demo | Client B (drill) | Client B by hand |
|---|---|---|---|
| Weekly runs | 56, Sundays, UTC | 9, Mondays, Europe/Stockholm | 9 |
| Products tracked | 356 of 360 | 18 of 20 | 15 groceries + 3 laptops |
| Competitor stores | 10 | 3 | 3 |
| Grocery listings, cheaper than us | 668, 460 | 25, 8 | 25, 8 |
| Price changes (cuts, rises) | 127 (52, 75) | 9 (4, 5) | 9 (4, 5) |
| Caught by the first run that could see them | 100% | 100% | |
| Undercuts | 17 (threshold 0%) | 2 (threshold 10%), caught by the runs of 7 Sep and 28 Sep | 2, same weeks |
| Name matching | 156 of 160 right, 0 wrong | 3 matched (scores 0.818, 0.917, 0.800), ProBook missed, MacBook unmatched | the same scores |
| Alert on the latest run | none that week | 1 undercut; no Gmail login, so logged and not sent | 1 |
| Power BI theme | "Competitor price tracker", `#2563EB` | "Landskrona Livs prices", `#0F766E`, page `#F0FDFA` | |
| Notebook | 0 errors | 0 errors; titles name Landskrona Livs, prices in SEK; "matching not scored" | |

**Clear failures**, one line each, run on the client B copy with `python tracker.py`, before the
warehouse is touched:

```
config/client.yaml is missing rules.undercut_pct
.env is missing DB_PASSWORD (copy .env.example to .env)
missing input file data/input/produkter.csv (inputs.catalogue in config/client.yaml)
data/input/produkter.csv is missing column(s): our_price
config/client.yaml competitor webscraper-io: no parser webscraper in parsers.py
config/client.yaml competitor willys: needs id, name, kind, city, and either parser and pages or open_prices_location
```

**Nothing hard-coded:** this search over the code (`tracker.py`, `config.py`, `theme.py`, `dags/`,
`sql/`, `powerbi/03-measures.dax`), the Power Query M code in `powerbi/01-power-query.md` and the
notebook's source cells finds nothing:

```
books-toscrape|webscraper-io|op-\d{4}|Safeway|Mountain View|books\.toscrape|webscraper\.io|5440|"tracker"|2025-09-07|Sample general store|\bUSD\b|\bGBP\b|#[0-9A-Fa-f]{6}|catalogue\.csv|match_truth\.csv|\b0\.6\b|Competitor price tracker|\bUTC\b|0 0 \* \* 0
```

On purpose outside the search: `docker-compose.yml` keeps the warehouse port, database and user, which
must match `warehouse.*` (its first lines say so); `parsers.py` is the per-site code (each parser knows
its site and currency); `make_catalogue.py` made the demo catalogue; `tests/` test the demo's parsers on
saved pages; the README, the diagrams in `docs/` and `powerbi/06-checks.md` describe the demo run.

**One addition to the template standard:** the undercut threshold reaches SQL as
`current_setting('client.undercut_pct')`, set with `ALTER DATABASE ... SET` by the first task of every
run rather than `set_config` in one session, because the alert, the notebook and Power BI read the
`undercut` view from their own connections.

**Nothing broke:** after the drill, the demo ran again from scratch on the template code (56 weekly
runs) and gave the same numbers: 356 products across 10 stores, 824 listings, 63.8% cheaper than us,
127 price changes (52 cuts, 75 rises), 17 undercuts, name matching 156 of 160 with 0 wrong, notebook
0 errors.
