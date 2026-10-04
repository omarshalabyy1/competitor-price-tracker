# 1. Power Query

The report reads the local warehouse: PostgreSQL on `localhost:5440`, database `tracker`, after
`docker compose up -d` and the `competitor_prices` DAG's catch-up (steps 1 to 5 of
[`08-build-checklist.md`](08-build-checklist.md)). Nothing is read from files.

Open Power BI Desktop, then **Home > Transform data** to open the Power Query editor. For each query
below: **Home > New source > Blank query**, rename it (right-click > Rename) to the name in the
heading, open **Home > Advanced editor**, delete what is there and paste the code.

| Query | Source | Columns | Renames | Load |
|---|---|---|---|---|
| `WarehouseServer` | parameter (text) | none | none | no (parameter) |
| `Product` | the `product` table | 8 (7 + `Key product`) | none | yes |
| `Store` | the `store` table | 4 | none | yes |
| `Daily Price` | the `daily_price` view, our products only | 6 | none | yes |
| `Price Change` | the `price_change` view | 11 (10 + `Direction`) | none | yes |
| `Price Gap` | the `price_gap` view | 8 (7 + `Position`) | none | yes |
| `Date` | generated from `Daily Price[observed_on]` | 5 | none | yes |

Why no renames: the column names match [`sql/schema.sql`](../sql/schema.sql) and the SQL in
`06-checks.md`, so a number on a card can be checked against the warehouse word for word. Visuals
show friendly names, set on the visual (`04-pages.md`).

Why the views and not the raw `price_observation` table: the views already hold one price per
listing per day, the changes and the gaps, written once in SQL and read the same way by the alert,
the notebook and this report.

Why every column gets a type: Power BI then never guesses, so a refresh after a new weekly run
cannot turn a price into text.

## The first connection

The first query you create asks for credentials: choose **Database**, user `tracker`, password =
`WAREHOUSE_PASSWORD` from the repo's `.env`, and apply them to `localhost:5440`. If Power BI says
it cannot connect with encryption, choose **OK** to connect without it: the warehouse listens on
your laptop only.

## WarehouseServer (parameter)

**Home > Manage parameters > New parameter**

- Name: `WarehouseServer`
- Type: Text
- Current value: `localhost:5440`

Why a parameter: if the port ever changes, it changes in one place.

## Product (loads)

Our catalogue: one row per product we sell.

```m
let
    Source = PostgreSQL.Database(WarehouseServer, "tracker"),
    product = Source{[Schema = "public", Item = "product"]}[Data],
    Typed = Table.TransformColumnTypes(product, {
        {"sku", type text}, {"name", type text}, {"category", type text}, {"barcode", type text},
        {"our_price", Currency.Type}, {"currency", type text}, {"is_key", type logical}}),
    KeyProduct = Table.AddColumn(Typed, "Key product", each if [is_key] then "Key" else "Other", type text)
in
    KeyProduct
```

`Key product` is a readable label for the slicer ("Key" or "Other") instead of True and False.

## Store (loads)

The competitor stores: one row per store.

```m
let
    Source = PostgreSQL.Database(WarehouseServer, "tracker"),
    store = Source{[Schema = "public", Item = "store"]}[Data],
    Kept = Table.SelectColumns(store, {"store_id", "name", "kind", "city"}),
    Typed = Table.TransformColumnTypes(Kept, {
        {"store_id", type text}, {"name", type text}, {"kind", type text}, {"city", type text}})
in
    Typed
```

## Daily Price (loads)

Every competitor price of our products: one row per listing per day.

```m
let
    Source = PostgreSQL.Database(WarehouseServer, "tracker"),
    daily_price = Source{[Schema = "public", Item = "daily_price"]}[Data],
    Ours = Table.SelectRows(daily_price, each [sku] <> null),
    Kept = Table.SelectColumns(Ours, {"store_id", "listing_key", "sku", "observed_on", "price", "is_discounted"}),
    Typed = Table.TransformColumnTypes(Kept, {
        {"store_id", type text}, {"listing_key", type text}, {"sku", type text},
        {"observed_on", type date}, {"price", Currency.Type}, {"is_discounted", type logical}})
in
    Typed
```

`Ours` drops the listings that are not one of our products: the report is about our catalogue.

## Price Change (loads)

Every price change on our products: one row per change.

```m
let
    Source = PostgreSQL.Database(WarehouseServer, "tracker"),
    price_change = Source{[Schema = "public", Item = "price_change"]}[Data],
    Kept = Table.SelectColumns(price_change, {
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

`Direction` says whether the change lowered or raised the price, for the Cuts and Rises measures.

## Price Gap (loads)

Each matched listing's latest price against ours: one row per listing.

```m
let
    Source = PostgreSQL.Database(WarehouseServer, "tracker"),
    price_gap = Source{[Schema = "public", Item = "price_gap"]}[Data],
    Typed = Table.TransformColumnTypes(price_gap, {
        {"store_id", type text}, {"listing_key", type text}, {"sku", type text},
        {"last_seen", type date}, {"competitor_price", Currency.Type}, {"our_price", Currency.Type},
        {"gap_pct", type number}}),
    Position = Table.AddColumn(Typed, "Position", each
        if [gap_pct] < 0 then "Cheaper than us" else if [gap_pct] = 0 then "Same price" else "Dearer than us", type text)
in
    Position
```

## Date (loads)

One row per day from the first to the last competitor price, with no gaps.

```m
let
    FirstDay = List.Min(#"Daily Price"[observed_on]),
    LastDay = List.Max(#"Daily Price"[observed_on]),
    Days = List.Dates(FirstDay, Duration.Days(LastDay - FirstDay) + 1, #duration(1, 0, 0, 0)),
    AsTable = Table.FromList(Days, Splitter.SplitByNothing(), {"Date"}),
    Typed = Table.TransformColumnTypes(AsTable, {{"Date", type date}}),
    Year = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
    Month = Table.AddColumn(Year, "Month", each Date.ToText([Date], "MMM yyyy", "en-US"), type text),
    MonthNumber = Table.AddColumn(Month, "Month Number", each Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    WeekStart = Table.AddColumn(MonthNumber, "Week Start", each Date.StartOfWeek([Date], Day.Sunday), type date)
in
    WeekStart
```

Why the weeks start on Sunday: the weekly runs cover Sunday to Sunday, so a week here is the same
week as a run.

**Home > Close & apply.** Then go to [`02-model.md`](02-model.md).

Prices stay in each store's own currency (the books shop is in GBP, everything else in USD), so
the report compares prices as percentages or one product at a time, never as sums across stores.
