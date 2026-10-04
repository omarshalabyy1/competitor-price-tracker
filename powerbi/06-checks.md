# 6. Checks

The numbers each card must show, with no slicer selected, from the run of 4 October 2026 (the
weekly runs from 7 September 2025 to 4 October 2026). They are the notebook's numbers
([analysis.ipynb](../analysis/analysis.ipynb)); the SQL under each table gives the same
numbers straight from the warehouse. If a card differs, the step named in the last column is
where to look.

A later weekly run adds prices, so after a refresh the numbers can grow; run the SQL again to
get the new ones.

## Page 1 · Price gaps

| Card | Must show | If not, check |
|---|---|---|
| Products tracked | 356 | Price Gap query; relationship Product → Price Gap |
| Competitor stores | 10 | Price Gap query |
| Listings compared | 824 | Price Gap query |
| Cheaper than us | 63.8% (526 of 824) | `Cheaper Than Us` filter is `gap_pct < 0` |
| Average gap | -8.2% | `Average Gap` divides by 100; format 0.0% |

```sql
SELECT count(DISTINCT sku) AS products_tracked, count(DISTINCT store_id) AS stores,
       count(*) AS listings, count(*) FILTER (WHERE gap_pct < 0) AS cheaper_than_us,
       round(avg((gap_pct < 0)::int) * 100, 1) AS share_cheaper_pct, round(avg(gap_pct), 1) AS average_gap_pct
FROM price_gap;
```

With the Store slicer on **Walmart Supercenter**: 41 listings, 88% cheaper than us (36), average
gap -14.0%. On **Books to Scrape**: 96 listings, 51% cheaper (49), average gap -0.5%.

## Page 2 · Price changes

| Card | Must show | If not, check |
|---|---|---|
| Price changes | 127 | Price Change query (no filter in Power Query) |
| Cuts | 52 | `Direction` column in the Price Change query |
| Rises | 75 | `Direction` column |
| Undercuts on key products | 17 | `is_undercut` typed as True/False |
| Average change | 0.9% | `Average Change` divides by 100 |

```sql
SELECT count(*) AS price_changes, count(*) FILTER (WHERE new_price < old_price) AS cuts,
       count(*) FILTER (WHERE new_price > old_price) AS rises, count(*) FILTER (WHERE is_undercut) AS undercuts,
       round(avg(change_pct), 1) AS average_change_pct
FROM price_change;
```

With the Products slicer on **Key**: 38 changes, 17 undercuts. On **Other**: 89 changes, 0 undercuts.

Column chart: the tallest bars are the week of 9 August 2026 (1 cut, 26 rises), 1 February 2026
(20 cuts, 1 rise) and 9 November 2025 (11 cuts, 9 rises).

Line chart, Product slicer on **Original Sichuan Chili Crisp**, Store slicer on **Walmart
Supercenter**: the price is 10.48 from February 2025 to November 2025, then 9.98 from 23 January
2026; the dashed "Our price" line is at 11.59.

```sql
SELECT d.observed_on, d.price
FROM daily_price d JOIN store s USING (store_id)
WHERE d.sku = 'GRO-0001' AND s.name = 'Walmart Supercenter'
ORDER BY d.observed_on;
```

Run the SQL in any SQL tool on `localhost:5440`, database `tracker`, user `tracker`, or with
`docker compose exec warehouse psql -U tracker -d tracker`.
