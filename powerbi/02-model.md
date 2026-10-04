# 2. Model

A small star: three facts, each with its own grain, sharing the Product, Store and Date
dimensions. Every relationship is one-to-many, single direction, from the dimension to the fact.

## Tables

| Table | Kind | Grain | Key |
|---|---|---|---|
| Product | Dimension | one row per product we sell | `sku` |
| Store | Dimension | one row per competitor store | `store_id` |
| Date | Dimension (DAX) | one row per day | `Date` |
| Daily Price | Fact | one competitor price per listing per day | `store_id` + `listing_key` + `observed_on` |
| Price Change | Fact | one price change of a listing | `store_id` + `listing_key` + `observed_on` |
| Price Gap | Fact (snapshot) | one listing's latest price against ours | `store_id` + `listing_key` |

## The Date table

Modeling → New table → paste:

```dax
Date =
VAR FirstDay = MIN ( 'Daily Price'[observed_on] )
VAR LastDay = MAX ( 'Daily Price'[observed_on] )
RETURN
    ADDCOLUMNS (
        CALENDAR ( FirstDay, LastDay ),
        "Year", YEAR ( [Date] ),
        "Month", FORMAT ( [Date], "mmm yyyy" ),
        "Month Number", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
        "Week Start", [Date] - WEEKDAY ( [Date], 1 ) + 1
    )
```

Then: select the table → Table tools → **Mark as date table** → column `Date`.
Select `Month` → Column tools → **Sort by column** → `Month Number`.

## Relationships

Model view → Manage relationships → New, one by one:

| From (one) | To (many) | Cardinality | Cross filter |
|---|---|---|---|
| Product[sku] | Daily Price[sku] | One to many | Single |
| Product[sku] | Price Change[sku] | One to many | Single |
| Product[sku] | Price Gap[sku] | One to many | Single |
| Store[store_id] | Daily Price[store_id] | One to many | Single |
| Store[store_id] | Price Change[store_id] | One to many | Single |
| Store[store_id] | Price Gap[store_id] | One to many | Single |
| Date[Date] | Daily Price[observed_on] | One to many | Single |
| Date[Date] | Price Change[observed_on] | One to many | Single |

Price Gap has no date: it is the latest price only, so it answers "where do we stand now".

## Hide, rename, format

- Hide in report view: every `sku` and `store_id` in the three facts, `listing_key` everywhere,
  `Product[is_key]` (use `Key product`), `Product[barcode]`, `Date[Month Number]`.
- Rename for the report: `Product[name]` → `Product`, `Store[name]` → `Store`,
  `Store[kind]` → `Store kind`, `Product[category]` → `Category`.
- Formats: every price column `0.00`; `change_pct` and `gap_pct` `0.0` (they are already in
  percent, so -4.5 means 4.5% lower); dates `d mmm yyyy`; `caught_week` `d mmm yyyy`.
- Display folders: the measures go in the folders named in [03-measures.dax](03-measures.dax).
  Create one table to hold them: Home → Enter data → name it `Measures`, one empty column, Load;
  then move each measure there (Measure tools → Home table) and hide the empty column.

Next: [03-measures.dax](03-measures.dax).
