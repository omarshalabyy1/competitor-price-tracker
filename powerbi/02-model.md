# 2. The model

Open **Model view** (the third icon on the left).

## Tables

Row counts are from the run of 4 October 2026 (see `06-checks.md`).

| Table | Grain (one row per) | Key | Rows |
|---|---|---|---|
| `Product` | product we sell | `sku` | 360 |
| `Store` | competitor store | `store_id` | 11 |
| `Date` | day, 2024-07-19 to 2026-10-04 | `Date` | 808 |
| `Daily Price` | competitor price of our product, per listing per day | `store_id` + `listing_key` + `observed_on` | 1,018 |
| `Price Change` | price change of one listing | `store_id` + `listing_key` + `observed_on` | 127 |
| `Price Gap` | listing's latest price against ours | `store_id` + `listing_key` | 824 |
| `_Measures` | holds the measures only | none | 1 (hidden) |

A small star: three facts that each keep their own grain, sharing the Product, Store and Date
dimensions. The `_Measures` table is created in step 3 (`03-measures.dax`). There are no
calculated columns and no calculated tables: every column comes from Power Query.

`Store` has 11 rows but only 10 stores show numbers: no product of ours is matched at the eleventh
(Costco), which is a real result of the matching, not an error.

## Mark the date table

Select the `Date` table, then **Table tools > Mark as date table**, and pick the `Date` column.

Why: the `Date` table has one row per day with no gaps, so days, weeks and months group correctly.
Turn off **File > Options and settings > Options > Current file > Data load > Auto date/time** so
Power BI does not add hidden date tables of its own.

## Relationships

Drag each "one" column onto its "many" column, then open the relationship (double-click the line)
and check the settings.

| From (one) | To (many) | Cardinality | Cross-filter direction | Active | Why |
|---|---|---|---|---|---|
| `Product[sku]` | `Daily Price[sku]` | One to many | Single | Yes | Product slicers filter the price history |
| `Product[sku]` | `Price Change[sku]` | One to many | Single | Yes | ...the changes |
| `Product[sku]` | `Price Gap[sku]` | One to many | Single | Yes | ...and the gaps |
| `Store[store_id]` | `Daily Price[store_id]` | One to many | Single | Yes | One Store slicer filters the price history |
| `Store[store_id]` | `Price Change[store_id]` | One to many | Single | Yes | ...the changes |
| `Store[store_id]` | `Price Gap[store_id]` | One to many | Single | Yes | ...and the gaps |
| `Date[Date]` | `Daily Price[observed_on]` | One to many | Single | Yes | The price history runs on the Date table |
| `Date[Date]` | `Price Change[observed_on]` | One to many | Single | Yes | A change is dated by the day the new price was on the shelf |

Power BI may create some of these on its own when you close Power Query. Delete any other
relationship it made (for example between `Price Change` and `Price Gap` on `store_id`): a second
path between the facts makes the model ambiguous.

Why single direction everywhere: filters flow from the small tables (Product, Store, Date) to the
facts, never back, so every number has one meaning.

Why `Price Gap` has no Date relationship: it holds each listing's latest price only, so it answers
"where do we stand now"; filtering it by a past date would mean nothing.

## Hide columns

Hide the columns a report builder should not pick, so slicers and axes always use the dimension
(right-click > Hide in report view):

- `sku` and `store_id` in `Daily Price`, `Price Change` and `Price Gap`: use `Product` and `Store`.
- `listing_key` in the three facts: an internal key (a page address or a barcode).
- `Daily Price[observed_on]`: use the `Date` columns.
- `Product[is_key]`: use `Product[Key product]`.
- `Product[barcode]`, `Product[currency]`, `Store[city]`: not used in the report.
- `Date[Month Number]`: used only for sorting.
- The empty column of `_Measures` (after step 3).

`Price Change[observed_on]` stays visible: the changes table on page 2 shows it as the date of
each change.

## Sort by column

Select `Date[Month]`, then **Column tools > Sort by column > Month Number**, so months run in
calendar order, not alphabetically.

## Column formats

Set in **Column tools > Format** with the column selected.

| Column | Format | Why |
|---|---|---|
| `Product[our_price]`, `Daily Price[price]`, `Price Change[old_price]`, `Price Change[new_price]`, `Price Gap[competitor_price]`, `Price Gap[our_price]` | Fixed decimal, 2 decimals, no currency symbol | Prices to the cent; no symbol because the books shop is in GBP and the rest in USD |
| `Price Change[change_pct]`, `Price Gap[gap_pct]` | Decimal number, 1 decimal | Already in percent: -25.0 means 25% lower |
| `Date[Date]`, `Price Change[observed_on]`, `Price Change[caught_week]`, `Price Gap[last_seen]` | Short date (`yyyy-mm-dd`) | Same as the warehouse and the checks |
| `Date[Year]` | Whole number, thousands separator off | A year, not a count |

## Display folders

Set on each measure in step 3 (**Properties pane > Display folder**):

| Folder | Measures |
|---|---|
| Gaps | Products Tracked, Stores Tracked, Listings Compared, Cheaper Than Us, Share Cheaper Than Us, Average Gap |
| Changes | Price Changes, Price Cuts, Price Rises, Undercuts, Average Change |
| History | Competitor Price, Our Price |
