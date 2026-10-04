# 4. Pages and visuals

Canvas: 16:9, 1280 × 720 (the default). Set each visual's position and size in **Format > General >
Properties**. `x, y, w, h` are in pixels from the top-left corner. Apply the theme (`05-theme.json`)
first so colours and fonts are already right. Colours are named by theme slot: Theme colour 1 is the
blue, 2 the navy, 4 the slate grey, 6 the pale blue.

Rename the pages (double-click the tab) to **Price gaps** and **Price changes**.

Number formats come from each measure's format string (`03-measures.dax`), so no visual needs its own
format. On every card set **Format > Visual > Callout value > Display units: None**, so the card
shows the full number as in `06-checks.md`. Visuals are listed in build order; the `#` is used in
`07-interactions.md`.

## Page 1: Price gaps

Where we stand against each competitor right now, product by product.

| # | Visual | x, y, w, h | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 24, 16, 600, 52 | "Where we stand against competitors" | Font 20, bold |
| 2 | Slicer | 640, 12, 148, 56 | Field: `Product[category]` | Slicer settings > Style: Dropdown. Selection: multi-select with Ctrl, "Select all" on. Header text "Category" |
| 3 | Slicer | 796, 12, 148, 56 | Field: `Store[kind]` | Style: Dropdown. Multi-select with Ctrl. Header text "Store kind" |
| 4 | Slicer | 952, 12, 148, 56 | Field: `Product[Key product]` | Style: Tile. Multi-select with Ctrl. Header text "Products" |
| 5 | Slicer | 1108, 12, 148, 56 | Field: `Store[name]` | Style: Dropdown. Multi-select with Ctrl, "Select all" on. Header text "Store" |
| 6 | Card | 24, 84, 240, 96 | `[Products Tracked]` | Category label on, renamed on the visual to "Products tracked" |
| 7 | Card | 272, 84, 240, 96 | `[Stores Tracked]` | Category label "Competitor stores" |
| 8 | Card | 520, 84, 240, 96 | `[Listings Compared]` | Category label "Listings compared" |
| 9 | Card | 768, 84, 240, 96 | `[Share Cheaper Than Us]` | Category label "Cheaper than us" |
| 10 | Card | 1016, 84, 240, 96 | `[Average Gap]` | Category label "Average gap (below 0: they are cheaper)" |
| 11 | Matrix | 24, 196, 820, 508 | Rows: `Product[name]`; Columns: `Store[name]`; Values: `[Average Gap]` | Title "Gap against our price, by product and store". Row and column subtotals off. Sort by `name`, ascending. Conditional formatting > Background color on `Average Gap`: Format style Gradient, tick "Add a middle color"; Minimum: Number -0.2, Theme colour 1; Middle: Number 0, White; Maximum: Number 0.2, Theme colour 4 |
| 12 | Clustered bar chart | 860, 196, 396, 508 | Y-axis: `Store[name]`; X-axis: `[Share Cheaper Than Us]`; Tooltips: `[Listings Compared]`, `[Average Gap]` | Title "Share of listings cheaper than us". Sort by Share Cheaper Than Us, descending. Data labels on. Bars Theme colour 1 |

In the matrix, blue cells are where a competitor is cheaper than us, the darker the cheaper; grey
cells are where it is dearer. Most cells are empty: each store sells only some of our products.

## Page 2: Price changes

What competitors changed, which weekly run caught it, and which changes were undercuts.

| # | Visual | x, y, w, h | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 24, 16, 600, 52 | "What competitors changed, week by week" | Font 20, bold |
| 2 | Slicer | 640, 12, 148, 56 | Field: `Product[category]` | Same as page 1 #2 (it is synced, see below) |
| 3 | Slicer | 796, 12, 148, 56 | Field: `Store[name]` | Same as page 1 #5 (synced) |
| 4 | Slicer | 952, 12, 148, 56 | Field: `Product[Key product]` | Same as page 1 #4 (synced) |
| 5 | Slicer | 1108, 12, 148, 56 | Field: `Product[name]` | Style: Dropdown. Selection: **Single select** on. Search on (slicer menu `...` > Search). Header text "Product (history)" |
| 6 | Card | 24, 84, 240, 96 | `[Price Changes]` | Category label "Price changes" |
| 7 | Card | 272, 84, 240, 96 | `[Price Cuts]` | Category label "Cuts" |
| 8 | Card | 520, 84, 240, 96 | `[Price Rises]` | Category label "Rises" |
| 9 | Card | 768, 84, 240, 96 | `[Undercuts]` | Category label "Undercuts on key products"; callout value colour Theme colour 1 |
| 10 | Card | 1016, 84, 240, 96 | `[Average Change]` | Category label "Average change" |
| 11 | Stacked column chart | 24, 196, 620, 250 | X-axis: `Price Change[caught_week]`; Y-axis: `[Price Cuts]`, `[Price Rises]` | Title "Changes caught by each weekly run". X-axis type: Categorical, sorted by `caught_week` ascending. Colours: Price Cuts Theme colour 1, Price Rises Theme colour 4. Legend: top. Data labels off |
| 12 | Line chart | 660, 196, 596, 250 | X-axis: `Date[Date]`; Y-axis: `[Competitor Price]`; Legend: `Store[name]` | Title "Price history of the picked product". X-axis type: Continuous. Markers on. Analytics pane > Y-axis constant line > Add > Value: fx > Field value `[Our Price]`; line colour Theme colour 2, style Dashed; Data label on, Text "Name", Name "Our price" |
| 13 | Table | 24, 462, 1232, 242 | `Product[sku]`, `Product[name]`, `Store[name]`, `Price Change[observed_on]`, `Price Change[old_price]`, `Price Change[new_price]`, `Price Change[change_pct]`, `Price Change[is_discounted]`, `Price Change[is_undercut]` | Title "Every change". In the field well, set `old_price`, `new_price` and `change_pct` to **Don't summarize** (arrow next to the field). Rename on the visual: sku "SKU", name "Product", name "Store", observed_on "Date", old_price "Was", new_price "Now", change_pct "Change %", is_discounted "On promotion", is_undercut "Undercut". Sort by Date, descending. Conditional formatting > Font color on Change %: Format style Rules; If value < 0 then Theme colour 1; If value > 0 then Theme colour 4. Totals off |

The line chart stays empty until a product is picked in slicer #5 (`Competitor Price` returns blank
for more than one product). `SKU` is in the table so two products with the same name, at the same
store on the same day, stay two rows.

## Sync the slicers

**View > Sync slicers**. For each slicer, tick **Sync** and **Visible** on the pages below:

| Slicer | Price gaps | Price changes | Why |
|---|---|---|---|
| Category (`Product[category]`) | yes | yes | One choice of products for both pages |
| Products (`Product[Key product]`) | yes | yes | Key products on both pages |
| Store (`Store[name]`) | yes | yes | One store on both pages |
| Store kind (`Store[kind]`) | yes | no | Page 1 only: the Store slicer already narrows page 2 |
| Product (`Product[name]`) | no | yes | Page 2 only: it drives the price history |

## Not used

No drill-through, bookmarks, buttons or tooltip pages, and no filters in the Filters pane (visual,
page or report level). "Our products only" is applied in Power Query (`Daily Price`), where a filter
cannot be cleared by accident. Two pages, five slicers and the interactions in `07-interactions.md`
answer both questions.
