# Power BI setup

The Python pipeline writes Power BI-ready tables to `output/powerbi/`.

## Build the data first

Offline demo:

```bash
financial-analytics demo
```

Live public data:

```bash
financial-analytics refresh --start-year 2020 --end-year 2026
```

## Create the report

1. Open Power BI Desktop.
2. Get Data -> Text/CSV.
3. Import the dimension and fact CSV files from `output/powerbi/`.
4. Set the date columns to Date type and numeric values to Decimal Number.
5. Create the relationships in `model.md`.
6. Mark `dim_date` as the date table.
7. Add the measures from `measures.dax`.
8. Build the pages in `report-pages.md`.
9. Save as a Power BI Project (`.pbip`) if you want the semantic model/report definitions under source control.

The repo keeps this design pack separate instead of pretending a hand-written PBIP has been validated by Power BI Desktop.
