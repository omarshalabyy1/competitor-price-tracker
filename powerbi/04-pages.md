# 4. Pages

Canvas: 16:9 (1280 × 720), the default. Apply the theme first: View → Themes → Browse for
themes → [05-theme.json](05-theme.json). Positions are x, y, width, height in pixels (Format →
General → Properties). Every visual title is on and written as below.

## Page 1 · Price gaps

Answers: where do we stand against each competitor right now, product by product?

| # | Visual | Position | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 20, 12, 900, 44 | "Where we stand against competitors" | Segoe UI Semibold 20 |
| 2 | Slicer (dropdown) | 20, 64, 230, 60 | Product[Category] | Multi-select with Ctrl; title "Category" |
| 3 | Slicer (tile) | 260, 64, 300, 60 | Store[Store kind] | Single select off; title "Store kind" |
| 4 | Slicer (tile) | 570, 64, 220, 60 | Product[Key product] | Title "Products" |
| 5 | Slicer (dropdown) | 800, 64, 230, 60 | Store[Store] | Title "Store" |
| 6 | Card | 20, 136, 240, 100 | [Products Tracked] | Category label "Products tracked" |
| 7 | Card | 270, 136, 240, 100 | [Stores Tracked] | Category label "Competitor stores" |
| 8 | Card | 520, 136, 240, 100 | [Listings Compared] | Category label "Listings compared" |
| 9 | Card | 770, 136, 240, 100 | [Share Cheaper Than Us] | Category label "Cheaper than us" |
| 10 | Card | 1020, 136, 240, 100 | [Average Gap] | Category label "Average gap (below 0 = they are cheaper)" |
| 11 | Matrix | 20, 248, 820, 460 | Rows Product[Product]; Columns Store[Store]; Values [Average Gap] | See below |
| 12 | Clustered bar chart | 850, 248, 410, 460 | Y axis Store[Store]; X axis [Share Cheaper Than Us] | See below |

**Matrix (11):** title "Gap against our price, by product and store". Values formatted 0.0%.
Cell elements → Background color → fx → Format style *Gradient*, based on [Average Gap]:
minimum number -0.2 colour `#DC2626`, center number 0 colour `#FFFFFF`, maximum number 0.2
colour `#0F766E`. Red means a competitor is cheaper than us. Row subtotals off, column
subtotals off. Sort by Product ascending.

**Bar chart (12):** title "Share of listings cheaper than us". Sort by [Share Cheaper Than
Us] descending. Data labels on, 0%. Bars colour `#F59E0B`.

Interactions: default (every visual filters the others).

## Page 2 · Price changes

Answers: what did competitors change, when did the weekly run catch it, and which changes were
undercuts on key products?

| # | Visual | Position | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 20, 12, 900, 44 | "What competitors changed, week by week" | Segoe UI Semibold 20 |
| 2 | Slicer (dropdown) | 20, 64, 230, 60 | Product[Category] | Title "Category" |
| 3 | Slicer (dropdown) | 260, 64, 230, 60 | Store[Store] | Title "Store" |
| 4 | Slicer (tile) | 500, 64, 220, 60 | Product[Key product] | Title "Products" |
| 5 | Slicer (dropdown) | 730, 64, 530, 60 | Product[Product] | Single select **on**, search on; title "Product (for the price history)" |
| 6 | Card | 20, 136, 240, 100 | [Price Changes] | Category label "Price changes" |
| 7 | Card | 270, 136, 240, 100 | [Price Cuts] | Category label "Cuts" |
| 8 | Card | 520, 136, 240, 100 | [Price Rises] | Category label "Rises" |
| 9 | Card | 770, 136, 240, 100 | [Undercuts] | Category label "Undercuts on key products"; callout colour `#DC2626` |
| 10 | Card | 1020, 136, 240, 100 | [Average Change] | Category label "Average change" |
| 11 | Stacked column chart | 20, 248, 620, 230 | X axis Price Change[caught_week]; Y axis [Price Cuts], [Price Rises] | See below |
| 12 | Line chart | 650, 248, 610, 230 | X axis Date[Date]; Y axis [Competitor Price]; Legend Store[Store] | See below |
| 13 | Table | 20, 488, 1240, 220 | Product[Product], Store[Store], Price Change[observed_on], [old_price], [new_price], [change_pct], [is_discounted], [is_undercut] | See below |

**Column chart (11):** title "Changes caught by each weekly run". X axis type *Categorical*,
format d mmm yyyy. Colours: Price Cuts `#F59E0B`, Price Rises `#64748B`. Legend top.

**Line chart (12):** title "Price history of the selected product". Analytics pane → Y-axis
constant line → Add → Value fx → field value [Our Price]; colour `#0F172A`, style dashed, data
label on with text "Our price". Markers on. It shows a price line per store for the one product
picked in slicer 5.

**Table (13):** rename the columns in the visual: observed_on "Date", old_price "Was",
new_price "Now", change_pct "Change %", is_discounted "On promotion", is_undercut "Undercut".
Sort by Date descending. Cell elements → Font color fx on Change %: rules, if value < 0 then
`#DC2626`, if value > 0 then `#0F766E`. Cell elements → Background color fx on Undercut: rule,
if value is True then `#FEF3C7`.

Interactions (Format → Edit interactions): select the column chart (11) and set the line chart
(12) to **None**, so clicking a week filters the table but not the price history.

## Slicer sync, drill-through, bookmarks

- View → Sync slicers: Product[Category] and Product[Key product] synced and visible on both
  pages. Store[Store] synced on both pages. Product[Product] is on page 2 only.
- No drill-through pages and no bookmarks: two pages answer the two questions.

When both pages are built, check every number against [06-checks.md](06-checks.md), then save
a screenshot of each page into [screenshots/](screenshots/) as `price-gaps.png` and
`price-changes.png`.
