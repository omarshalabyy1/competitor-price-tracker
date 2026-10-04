# 7. Interactions

## Report setting (once)

**File > Options and settings > Options > Current file > Report settings**: tick **Change default
visual interaction from cross highlighting to cross filtering**.

Why: clicking a bar then filters the other visuals to it instead of greying out part of each bar, so
every card shows the selected store's or week's real numbers.

## How to set a cell

Select the source visual (the one you click), then **Format > Edit interactions**. Each other visual
shows icons in its top-right corner: **Filter** (funnel) or **None** (circle with a line). Click the
one the table below says. Click **Edit interactions** again to finish.

Numbers are the visual `#` in `04-pages.md`. Text boxes (#1) take no part. Cards are never a source:
clicking a card selects nothing.

## Page 1: Price gaps

| Source (click) | Category #2 | Store kind #3 | Products #4 | Store #5 | Cards #6-10 | Gap matrix #11 | Store bar #12 |
|---|---|---|---|---|---|---|---|
| Category slicer #2 | | Filter | Filter | Filter | Filter | Filter | Filter |
| Store kind slicer #3 | Filter | | Filter | Filter | Filter | Filter | Filter |
| Products slicer #4 | Filter | Filter | | Filter | Filter | Filter | Filter |
| Store slicer #5 | Filter | Filter | Filter | | Filter | Filter | Filter |
| Gap matrix #11 | None | None | None | None | Filter | | Filter |
| Store bar #12 | None | None | None | None | Filter | Filter | |

Why None on the slicers: a click on a chart should not shrink a slicer's list, so every category,
store and product stays pickable.

What a click changes:

- **A store in #12:** the cards and the matrix show that store only (check C7).
- **A cell in #11 (product and store):** the cards show that one listing; the bar shows that store.

## Page 2: Price changes

| Source (click) | Category #2 | Store #3 | Products #4 | Product #5 | Cards #6-10 | Weekly columns #11 | Price history #12 | Changes table #13 |
|---|---|---|---|---|---|---|---|---|
| Category slicer #2 | | Filter | Filter | Filter | Filter | Filter | Filter | Filter |
| Store slicer #3 | Filter | | Filter | Filter | Filter | Filter | Filter | Filter |
| Products slicer #4 | Filter | Filter | | Filter | Filter | Filter | Filter | Filter |
| Product slicer #5 | None | None | None | | None | None | Filter | Filter |
| Weekly columns #11 | None | None | None | None | Filter | | None | Filter |
| Price history #12 | None | None | None | None | None | None | | None |
| Changes table #13 | None | None | None | None | None | None | None | |

What a click changes:

- **A product in #5:** only the price history and the table follow it; the cards and the weekly
  columns keep counting every product in the other slicers, so picking a product to look at never
  changes the totals (check C14).
- **A week in #11:** the cards and the table show that run's changes (check C13). The price history
  keeps its full timeline, so the week can be seen in context.
- **A point in #12 or a row in #13:** nothing. The chart and the table are for reading.

## Not used

- Drill-through pages: none. The Product slicer and the table already show one product's changes.
- Bookmarks and buttons: none.
- Tooltip pages: none. The store bar (page 1 #12) uses the default tooltip with Listings Compared and
  Average Gap added to its Tooltips well.
- Filters pane: no visual-, page- or report-level filters. "Our products only" is in Power Query.
