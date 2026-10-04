# Power BI report

Two pages on top of the warehouse:

1. **Price gaps:** where we stand against each competitor right now, product by product: how
   many listings are cheaper than us and by how much.
2. **Price changes:** what competitors changed, which weekly run caught it, which changes were
   undercuts on key products, and one product's price history against ours.

Build it in Power BI Desktop from an empty report, in this order, copying and pasting as you go:

| Step | File | What you do |
|---|---|---|
| 1 | [01-power-query.md](01-power-query.md) | Connect to the warehouse and paste the five queries |
| 2 | [02-model.md](02-model.md) | Add the Date table, the relationships, hide and format columns |
| 3 | [03-measures.dax](03-measures.dax) | Paste the measures, one at a time |
| 4 | [05-theme.json](05-theme.json) | Apply the theme (View → Themes → Browse for themes) |
| 5 | [04-pages.md](04-pages.md) | Place every visual with its fields and settings |
| 6 | [06-checks.md](06-checks.md) | Check every card shows the right number |

Then save the report here as `competitor-prices.pbix` and one screenshot per page in
[screenshots/](screenshots/).

The warehouse must be running (`docker compose up -d` in the repo root) while you build or
refresh the report.
