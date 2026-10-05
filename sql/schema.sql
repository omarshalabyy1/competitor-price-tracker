-- The warehouse: the client's products, the competitor stores, what each competitor sells (listing),
-- every price ever seen (price_observation, append-only) and the views the alert and Power BI read.
-- Safe to run again: the load_reference step runs it at the start of every weekly run.

CREATE TABLE IF NOT EXISTS product (          -- the client's own catalogue (inputs.catalogue in data/input/)
    sku       text PRIMARY KEY,
    name      text NOT NULL,
    category  text NOT NULL,
    barcode   text UNIQUE,                    -- grocery products; text keeps the leading zeros
    our_price numeric(10, 2) NOT NULL CHECK (our_price > 0),
    currency  text NOT NULL,
    is_key    boolean NOT NULL                -- key products get the undercut alert
);

CREATE TABLE IF NOT EXISTS store (            -- competitor stores (competitors in config/client.yaml)
    store_id   text PRIMARY KEY,
    name       text NOT NULL,
    kind       text NOT NULL,                 -- 'web shop' or 'grocery store'
    city       text NOT NULL,
    source     text NOT NULL CHECK (source IN ('web shop pages', 'open prices')),
    source_ref text NOT NULL                  -- the shop's address, or its Open Prices location id
);

CREATE TABLE IF NOT EXISTS listing (          -- one product as one competitor sells it
    store_id    text NOT NULL REFERENCES store,
    listing_key text NOT NULL,                -- product page URL (web shops) or barcode (grocery stores)
    title       text NOT NULL,
    sku         text REFERENCES product,      -- set by the match step; NULL = not a product we sell
    match_score numeric(4, 3),                -- how alike the names are; 1 for a barcode match
    PRIMARY KEY (store_id, listing_key)
);

CREATE TABLE IF NOT EXISTS price_observation ( -- every price seen, never updated or deleted
    store_id      text NOT NULL,
    listing_key   text NOT NULL,
    observed_on   date NOT NULL,              -- the day the price was on the shelf or the page
    price         numeric(10, 2) NOT NULL CHECK (price > 0),
    currency      text NOT NULL,
    is_discounted boolean NOT NULL,
    source_id     text NOT NULL,              -- Open Prices price id, or 'page' for a page read
    published_at  timestamptz NOT NULL,       -- when the price could first be read
    run_week      date NOT NULL,              -- the weekly run that loaded it (first day of its week)
    PRIMARY KEY (store_id, listing_key, observed_on, source_id),
    FOREIGN KEY (store_id, listing_key) REFERENCES listing
);

CREATE TABLE IF NOT EXISTS alert_sent (       -- one row per alert email
    run_week  date PRIMARY KEY,
    sent_at   timestamptz NOT NULL,
    undercuts integer NOT NULL
);

-- One price per listing per day, with the product it was matched to (sku NULL = not ours).
-- When two shoppers report different prices for the same day, the lower one wins: it is the
-- price a customer could pay.
CREATE OR REPLACE VIEW daily_price AS
SELECT DISTINCT ON (o.store_id, o.listing_key, o.observed_on)
       o.store_id, o.listing_key, l.sku, o.observed_on, o.price, o.currency, o.is_discounted,
       o.published_at, o.run_week
FROM price_observation o
JOIN listing l USING (store_id, listing_key)
ORDER BY o.store_id, o.listing_key, o.observed_on, o.price, o.published_at;

-- Every price change on our products: a day's price that differs from the listing's previous day
-- with a price. caught_week is the run that had both prices, so the first run that could see it.
-- An undercut: a competitor cut a key product's price to more than rules.undercut_pct percent below
-- ours (client.undercut_pct, set on the database by load_reference).
CREATE OR REPLACE VIEW price_change AS
SELECT t.store_id, t.listing_key, t.sku, t.observed_on, t.old_price, t.price AS new_price,
       round((t.price - t.old_price) / t.old_price * 100, 1) AS change_pct,
       t.currency, t.is_discounted, t.published_at, t.caught_week,
       p.is_key AND t.price < t.old_price
           AND t.price < p.our_price * (1 - current_setting('client.undercut_pct')::numeric / 100) AS is_undercut
FROM (
    SELECT d.*,
           lag(d.price) OVER w AS old_price,
           greatest(d.run_week, lag(d.run_week) OVER w) AS caught_week
    FROM daily_price d
    WINDOW w AS (PARTITION BY d.store_id, d.listing_key ORDER BY d.observed_on)
) t
JOIN product p USING (sku)
WHERE t.old_price IS NOT NULL AND t.price <> t.old_price;

-- The latest price of every matched listing against our own price.
CREATE OR REPLACE VIEW price_gap AS
SELECT DISTINCT ON (d.store_id, d.listing_key)
       d.store_id, d.listing_key, d.sku, d.observed_on AS last_seen, d.price AS competitor_price,
       p.our_price, round((d.price - p.our_price) / p.our_price * 100, 1) AS gap_pct
FROM daily_price d
JOIN product p USING (sku)
ORDER BY d.store_id, d.listing_key, d.observed_on DESC;

-- What the alert email lists.
CREATE OR REPLACE VIEW undercut AS
SELECT c.caught_week, s.name AS store, p.sku, p.name AS product, c.observed_on,
       c.old_price, c.new_price, p.our_price
FROM price_change c
JOIN product p USING (sku)
JOIN store s USING (store_id)
WHERE c.is_undercut;
