# 8. Build checklist

Follow in order. A **Check** line is a number to verify before going on (all in `06-checks.md`); if
it is off, fix that step first.

## Prepare the warehouse

1. Start Docker Desktop. In the repo folder, if there is no `.env` yet, copy `.env.example` to `.env`
   and set `WAREHOUSE_PASSWORD` to a password of your choice. Then run `docker compose up -d --build`.
2. Open Airflow at http://127.0.0.1:8090 and switch `competitor_prices` on (the toggle left of its
   name). It catches up one week at a time from 7 September 2025, about half an hour.
3. **Check:** in Airflow every run of `competitor_prices` is green, and the newest one covers last
   week. Then **C1** with the SQL in `06-checks.md`.
4. If today is later than 11 October 2026, the catch-up reached weeks after the ones in
   `06-checks.md`: run the notebook (`jupyter lab analysis/analysis.ipynb`, then **Run > Run All
   Cells**) and, for every check below, use the notebook's numbers and the SQL in `06-checks.md`
   instead of the numbers written there.

## Power BI settings

5. Open Power BI Desktop, then **Blank report**.
6. **File > Options and settings > Options > Current file**:
   - **Data load:** untick **Auto date/time**.
   - **Report settings:** tick **Change default visual interaction from cross highlighting to cross
     filtering**.
7. **View > Themes > Browse for themes**, pick `powerbi/05-theme.json`.

## Power Query (`01-power-query.md`)

8. **Home > Transform data**. Create the `WarehouseServer` parameter (`127.0.0.1:5440`).
9. Create the queries in this order, pasting each one's M code: `Product`, `Store`, `Daily Price`,
   `Price Change`, `Price Gap`, `Date`. The first asks for credentials: Database, user `tracker`, the
   password from `.env`.
10. **Home > Close & apply**.
11. Open **Table view** (second icon on the left) and click each table; the row count is at the
    bottom left.
    **Check C2:** Product 360 · Store 11 · Date 808 · Daily Price 1,018 · Price Change 127 · Price
    Gap 824.

## Model (`02-model.md`)

12. **Model view**: delete any relationship Power BI made on its own, then create the eight
    relationships in the table, each One to many, Single, Active.
13. Mark `Date` as the date table (column `Date`).
14. Hide the columns listed under "Hide columns".
15. Sort `Date[Month]` by `Month Number`.
16. Set the column formats.

## Measures (`03-measures.dax`)

17. **Home > Enter data**, name the table `_Measures`, **Load**.
18. Paste the 13 measures one by one into `_Measures`, setting each one's format string and display
    folder. Hide the empty column.
19. On a blank page, drop a card with `[Products Tracked]` and one with `[Price Changes]` (Display
    units: None).
    **Check:** 356 and 127. Delete both cards.

## Page 1: Price gaps (`04-pages.md`)

20. Rename the page to **Price gaps**. Build visuals 1 to 12 in order, with their position and size.
21. **Check C3:** Products tracked 356 · Competitor stores 10 · Listings compared 824 · Cheaper than
    us 63.8% · Average gap -8.2%.
22. **Check C4:** the bar chart's labels, from Trader Joe's 100.0% down to Web Scraper test shop
    28.3%.
23. **Check C5:** Store kind on web shop, then on grocery store. Clear it.
24. **Check C6:** Products on Key, then on Other. Clear it.

## Page 2: Price changes (`04-pages.md`)

25. Add a page, rename it **Price changes**. Build visuals 1 to 13 in order.
26. **Check C8:** Price changes 127 · Cuts 52 · Rises 75 · Undercuts on key products 17 · Average
    change 0.9%.
27. **Check C9:** 24 columns; the tallest are 2026-08-09, 2026-02-01 and 2025-11-09.

## Slicers and interactions

28. **View > Sync slicers**: set each slicer as in the table under "Sync the slicers" in
    `04-pages.md`.
29. Set every interaction as in `07-interactions.md`, page by page.
30. **Check C7:** on page 1, click Walmart Supercenter in the bar chart: Products tracked 41 ·
    Cheaper than us 87.8% · Average gap -14.0%. Click it again to clear.
31. **Check C10, C11, C12:** on page 2, the Store slicer on Safeway (N Shoreline Blvd), then the
    Products slicer on Key and Other, then the Category slicer on Desserts. Clear each one after.
32. **Check C13:** click the 2026-02-01 column: Price changes 21 · Cuts 20 · Rises 1 · Undercuts 6,
    and 21 rows in the table. Click it again to clear.
33. **Check C14:** pick Original Sichuan Chili Crisp in the Product slicer: 5 store lines, Walmart
    Supercenter from 10.48 down to 9.98, Our price dashed at 11.59, cards unchanged.
34. **Check C15:** clear the Product slicer; the table's top rows are dated 2026-08-11.

## Save and screenshots

35. **File > Save as** `powerbi/competitor-prices.pbix`.
36. Export each page at 1280 × 720 (**File > Export > Export to PDF**, or a screenshot of the page)
    to `powerbi/screenshots/price-gaps.png` (no slicer selected) and
    `powerbi/screenshots/price-changes.png` (Original Sichuan Chili Crisp picked in the Product
    slicer, so the price history shows a line; the cards still show every product).
37. In the main `README.md`, replace the comment in the "Power BI" section with both images. Commit
    and push.
