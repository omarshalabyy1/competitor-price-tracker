# 1. Power Query

The report reads the warehouse's views directly, so it always shows the latest weekly run.
Start the stack first (`docker compose up -d`): the warehouse listens on `localhost:5440`.

**Get the connection in:** Home → Get data → PostgreSQL database. Server `localhost:5440`,
database `tracker`, Data connectivity mode **Import**. Credentials: Database, user `tracker`,
password = `WAREHOUSE_PASSWORD` from `.env`. If Power BI says it cannot connect with
encryption, choose **OK** to connect without it (the warehouse only listens on your laptop).
Close the Navigator without picking a table, then create the queries below.

For each query: Home → New source → Blank query → Advanced Editor → paste → rename the query to
the name in the heading.

| Query | Loads? | What it is | Grain |
|---|---|---|---|
| Warehouse | No (staging) | The connection, used by every other query | — |
| Product | Yes | Our catalogue | one row per product (`sku`) |
| Store | Yes | Competitor stores | one row per store (`store_id`) |
| Daily Price | Yes | Every competitor price of our products | one row per listing per day |
| Price Change | Yes | Every price change of our products | one row per change |
| Price Gap | Yes | Each listing's latest price against ours | one row per listing |

## Warehouse

Right-click the query → untick **Enable load**: it is only the connection.

```m
let
    Source = PostgreSQL.Database("localhost:5440", "tracker")
in
    Source
```

## Product

```m
let
    Source = Warehouse{[Schema = "public", Item = "product"]}[Data],
    Typed = Table.TransformColumnTypes(Source, {
        {"sku", type text}, {"name", type text}, {"category", type text}, {"barcode", type text},
        {"our_price", Currency.Type}, {"currency", type text}, {"is_key", type logical}}),
    KeyProduct = Table.AddColumn(Typed, "Key product", each if [is_key] then "Key" else "Other", type text)
in
    KeyProduct
```

Applied steps: `Source` (the table), `Typed` (column types), `KeyProduct` (a readable label for
the slicer).

## Store

```m
let
    Source = Warehouse{[Schema = "public", Item = "store"]}[Data],
    Kept = Table.SelectColumns(Source, {"store_id", "name", "kind", "city"}),
    Typed = Table.TransformColumnTypes(Kept, {
        {"store_id", type text}, {"name", type text}, {"kind", type text}, {"city", type text}})
in
    Typed
```

## Daily Price

```m
let
    Source = Warehouse{[Schema = "public", Item = "daily_price"]}[Data],
    Ours = Table.SelectRows(Source, each [sku] <> null),
    Kept = Table.SelectColumns(Ours, {"store_id", "listing_key", "sku", "observed_on", "price", "is_discounted"}),
    Typed = Table.TransformColumnTypes(Kept, {
        {"store_id", type text}, {"listing_key", type text}, {"sku", type text},
        {"observed_on", type date}, {"price", Currency.Type}, {"is_discounted", type logical}})
in
    Typed
```

`Ours` keeps only the listings matched to our products; the rest of what competitors sell is not
in the report.

## Price Change

```m
let
    Source = Warehouse{[Schema = "public", Item = "price_change"]}[Data],
    Kept = Table.SelectColumns(Source, {
        "store_id", "listing_key", "sku", "observed_on", "old_price", "new_price", "change_pct",
        "is_discounted", "caught_week", "is_undercut"}),
    Typed = Table.TransformColumnTypes(Kept, {
        {"store_id", type text}, {"listing_key", type text}, {"sku", type text},
        {"observed_on", type date}, {"old_price", Currency.Type}, {"new_price", Currency.Type},
        {"change_pct", type number}, {"is_discounted", type logical}, {"caught_week", type date},
        {"is_undercut", type logical}}),
    Direction = Table.AddColumn(Typed, "Direction", each if [new_price] < [old_price] then "Cut" else "Rise", type text)
in
    Direction
```

## Price Gap

```m
let
    Source = Warehouse{[Schema = "public", Item = "price_gap"]}[Data],
    Typed = Table.TransformColumnTypes(Source, {
        {"store_id", type text}, {"listing_key", type text}, {"sku", type text},
        {"last_seen", type date}, {"competitor_price", Currency.Type}, {"our_price", Currency.Type},
        {"gap_pct", type number}}),
    Position = Table.AddColumn(Typed, "Position", each
        if [gap_pct] < 0 then "Cheaper than us" else if [gap_pct] = 0 then "Same price" else "Dearer than us", type text)
in
    Position
```

Close & Apply. Then go to [02-model.md](02-model.md).

Prices stay in each store's own currency (the books shop is in GBP, everything else in USD), so
the report compares prices only as percentages or one product at a time, never as sums.
