# 6. Checks: the numbers the report must show

Every number below comes from `analysis/analysis.ipynb` and from the SQL under each section, run on
the warehouse after the weekly runs of 7 September 2025 to 4 October 2026. Check with no slicer
selected unless a check says otherwise. If a card is off, the usual causes are a missing
relationship, a wrong column type in Power Query, or a filter left on a slicer.

**Building on a later date?** The tracker reads live prices, so a fresh `docker compose up` catches
up to a later week and the numbers grow. Then run the notebook once: section 9 prints the new card
numbers, and the SQL under each section below gives the new value for every check. Compare the report
with those, not with the numbers written here.

Run the SQL in any SQL tool on `127.0.0.1:5440`, database `tracker`, user `tracker`, or with
`docker compose exec warehouse psql -U tracker -d tracker`.

## The warehouse, before Power BI

**C1.** The catch-up is complete: 127 price changes and 824 compared listings.

```sql
SELECT (SELECT count(*) FROM price_change) AS price_changes, (SELECT count(*) FROM price_gap) AS listings;
```

**C2.** Rows per table after **Close & apply** (Table view, bottom left): Product 360 · Store 11 ·
Date 808 · Daily Price 1,018 · Price Change 127 · Price Gap 824.

```sql
SELECT (SELECT count(*) FROM product) AS product, (SELECT count(*) FROM store) AS store,
       (SELECT max(observed_on) - min(observed_on) + 1 FROM daily_price WHERE sku IS NOT NULL) AS date,
       (SELECT count(*) FROM daily_price WHERE sku IS NOT NULL) AS daily_price,
       (SELECT count(*) FROM price_change) AS price_change, (SELECT count(*) FROM price_gap) AS price_gap;
```

## Page 1: Price gaps

**C3.** Cards, no slicer: Products tracked 356 · Competitor stores 10 · Listings compared 824 ·
Cheaper than us 63.8% · Average gap -8.2%.

```sql
SELECT count(DISTINCT sku) AS products_tracked, count(DISTINCT store_id) AS stores, count(*) AS listings,
       round(avg((gap_pct < 0)::int) * 100, 1) AS share_cheaper_pct, round(avg(gap_pct), 1) AS average_gap_pct
FROM price_gap;
```

**C4.** Bar chart (#12) data labels, top to bottom: Trader Joe's 100.0% · Walmart Supercenter 87.8% ·
Smart & Final extra! 82.5% · Safeway (San Antonio Rd) 79.4% · Safeway (N Shoreline Blvd) 67.4% ·
99 Ranch Market 61.9% · Nob Hill Foods 58.2% · Ava's Market and Deli 55.6% · Books to Scrape 51.0% ·
Web Scraper test shop 28.3%. (Trader Joe's sells only 1 of our products: hover it, Listings
compared 1.)

```sql
SELECT s.name, count(*) AS listings, round(avg((gap_pct < 0)::int) * 100, 1) AS share_cheaper_pct
FROM price_gap g JOIN store s USING (store_id) GROUP BY s.name ORDER BY share_cheaper_pct DESC;
```

**C5.** Store kind slicer (#3) on **web shop**: Products tracked 156 · Competitor stores 2 · Listings
compared 156 · Cheaper than us 42.3% · Average gap 0.3%. On **grocery store**: 200 · 8 · 668 ·
68.9% · -10.1%. Clear the slicer.

**C6.** Products slicer (#4) on **Key**: Products tracked 74 · Listings compared 204 · Cheaper than
us 59.8% · Average gap -5.8%. On **Other**: 282 · 620 · 65.2% · -8.9%. Clear the slicer.

```sql
SELECT s.kind, count(DISTINCT g.sku) AS products, count(DISTINCT g.store_id) AS stores, count(*) AS listings,
       round(avg((gap_pct < 0)::int) * 100, 1) AS share_cheaper_pct, round(avg(gap_pct), 1) AS average_gap_pct
FROM price_gap g JOIN store s USING (store_id) GROUP BY s.kind;

SELECT p.is_key, count(DISTINCT g.sku) AS products, count(*) AS listings,
       round(avg((gap_pct < 0)::int) * 100, 1) AS share_cheaper_pct, round(avg(gap_pct), 1) AS average_gap_pct
FROM price_gap g JOIN product p USING (sku) GROUP BY p.is_key;
```

**C7.** Click **Walmart Supercenter** in the bar chart (#12): Products tracked 41 · Competitor
stores 1 · Listings compared 41 · Cheaper than us 87.8% · Average gap -14.0%. Click it again to clear.

## Page 2: Price changes

**C8.** Cards, no slicer: Price changes 127 · Cuts 52 · Rises 75 · Undercuts on key products 17 ·
Average change 0.9%.

```sql
SELECT count(*) AS price_changes, count(*) FILTER (WHERE new_price < old_price) AS cuts,
       count(*) FILTER (WHERE new_price > old_price) AS rises, count(*) FILTER (WHERE is_undercut) AS undercuts,
       round(avg(change_pct), 1) AS average_change_pct
FROM price_change;
```

**C9.** Column chart (#11): 24 weekly runs have a bar. The tallest are the week of 2026-08-09
(1 cut, 26 rises), 2026-02-01 (20 cuts, 1 rise) and 2025-11-09 (11 cuts, 9 rises).

```sql
SELECT caught_week, count(*) FILTER (WHERE new_price < old_price) AS cuts,
       count(*) FILTER (WHERE new_price > old_price) AS rises
FROM price_change GROUP BY caught_week ORDER BY count(*) DESC;
```

**C10.** Store slicer (#3) on **Safeway (N Shoreline Blvd)**: Price changes 93 · Cuts 37 · Rises 56 ·
Undercuts 12. Clear the slicer.

**C11.** Products slicer (#4) on **Key**: Price changes 38 · Undercuts 17. On **Other**: 89 · 0. Clear
the slicer.

**C12.** Category slicer (#2) on **Desserts**: Price changes 44 · Undercuts 12. Clear the slicer.

```sql
SELECT s.name, count(*) AS changes, count(*) FILTER (WHERE new_price < old_price) AS cuts,
       count(*) FILTER (WHERE new_price > old_price) AS rises, count(*) FILTER (WHERE is_undercut) AS undercuts
FROM price_change c JOIN store s USING (store_id) GROUP BY s.name ORDER BY changes DESC;

SELECT p.is_key, p.category, count(*) AS changes, count(*) FILTER (WHERE is_undercut) AS undercuts
FROM price_change c JOIN product p USING (sku) GROUP BY ROLLUP (p.is_key, p.category);
```

**C13.** Click the **2026-02-01** column in the column chart (#11): Price changes 21 · Cuts 20 ·
Rises 1 · Undercuts 6, and the table (#13) shows 21 rows, most of them ice cream at Safeway
(N Shoreline Blvd) cut from 4.00 to 3.00. Click the column again to clear.

```sql
SELECT p.name, s.name AS store, c.observed_on, c.old_price, c.new_price, c.is_undercut
FROM price_change c JOIN product p USING (sku) JOIN store s USING (store_id)
WHERE c.caught_week = '2026-02-01' ORDER BY c.observed_on DESC;
```

**C14.** Product slicer (#5) on **Original Sichuan Chili Crisp**: the line chart (#12) shows 5 stores.
The Walmart Supercenter line is 10.48 from 2025-02-06 to 2025-11-14, then 9.98 from 2026-01-23; the
dashed Our price line is at 11.59. The cards do not change (C8). Clear the slicer: the line chart is
empty again.

```sql
SELECT s.name AS store, d.observed_on, d.price
FROM daily_price d JOIN store s USING (store_id)
WHERE d.sku = 'GRO-0001' ORDER BY s.name, d.observed_on;
```

**C15.** Table (#13), sorted by Date descending: the top rows are dated 2026-08-11, three changes at
Safeway (N Shoreline Blvd): Celery seed, Bay Leaves and Chives. Its 127 rows match C8.
