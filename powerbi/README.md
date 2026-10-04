# Power BI: build the report step by step

The report reads the local warehouse and answers two questions:

1. **Price gaps:** where we stand against each competitor right now, product by product: how many
   listings are cheaper than us and by how much.
2. **Price changes:** what competitors changed, which weekly run caught it, which changes were
   undercuts on key products, and one product's price history against ours.

Everything below is copy and paste. **Start with [`08-build-checklist.md`](08-build-checklist.md)**:
37 numbered steps from starting the warehouse to the last screenshot, with a check number at each
point. It points to the other files:

| File | What it holds |
|---|---|
| [`01-power-query.md`](01-power-query.md) | The `WarehouseServer` parameter and six queries (M code) |
| [`02-model.md`](02-model.md) | Tables, date table, eight relationships, hidden columns, sort, formats, display folders, with the reason for each |
| [`03-measures.dax`](03-measures.dax) | The `_Measures` table and 13 measures, grouped by page |
| [`04-pages.md`](04-pages.md) | Two pages, 25 visuals: type, fields, position and size, settings, slicer sync |
| [`05-theme.json`](05-theme.json) | The theme: **View > Themes > Browse for themes**, pick this file |
| [`06-checks.md`](06-checks.md) | Checks C1 to C15: the numbers every card and chart must show, with the SQL behind each |
| [`07-interactions.md`](07-interactions.md) | Which visual filters which, per page |
| [`08-build-checklist.md`](08-build-checklist.md) | The build, step by step |

The theme is the one every portfolio project report shares (navy `#0E1630`, blue `#2563EB`, soft
grey page `#F4F6FB`), so the reports look like one family. The pages name colours by theme slot
(Theme colour 1 is the blue), never by hex code. The site's font, Geist, is not in Power BI's font
list, so the theme uses Segoe UI.

The warehouse must be running (`docker compose up -d` in the repo root) while you build or refresh
the report. After each Sunday's run, press **Refresh** in Power BI: that is the one click.

When the report is built:

- Save it as `powerbi/competitor-prices.pbix`.
- Export one image per page to `powerbi/screenshots/price-gaps.png` and
  `powerbi/screenshots/price-changes.png`.
- Add both images to the "Power BI" section of the main README.
