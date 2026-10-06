# Power BI semantic model draft

This is a design pack, not a generated PBIX/PBIT binary. It should be reviewed in Power BI Desktop before it is treated as final.

## Recommended imported tables

- `dim_company.csv`
- `dim_metric.csv`
- `dim_macro_series.csv`
- `dim_date.csv`
- `fact_financial_metric.csv`
- `fact_macro_indicator.csv`

The three `mart_*.csv` files are useful for reconciliation and quick analysis, but the main semantic model should use the facts and dimensions above.

## Relationships

| From | To | Cardinality | Direction |
| --- | --- | --- | --- |
| dim_company[company_key] | fact_financial_metric[company_key] | 1:* | Single |
| dim_metric[metric_key] | fact_financial_metric[metric_key] | 1:* | Single |
| dim_macro_series[series_key] | fact_macro_indicator[series_key] | 1:* | Single |
| dim_date[date] | fact_financial_metric[period_end] | 1:* | Single |
| dim_date[date] | fact_macro_indicator[observation_date] | 1:* | Single |

Mark `dim_date[date]` as the date table.

## Types

Set financial values to Decimal Number or Fixed Decimal depending on reporting preference. Keep raw USD values unscaled in the model and use display units in visuals rather than modifying source values.
