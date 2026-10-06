from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd

from financial_analytics.warehouse import query


EXPORT_QUERIES = {
    "dim_company": "SELECT * FROM dim_company ORDER BY company_key",
    "dim_metric": "SELECT * FROM dim_metric ORDER BY metric_key",
    "dim_macro_series": "SELECT * FROM dim_macro_series ORDER BY series_key",
    "fact_financial_metric": "SELECT * FROM fact_financial_metric ORDER BY company_key, fiscal_year, metric_key",
    "fact_macro_indicator": "SELECT * FROM fact_macro_indicator ORDER BY observation_date, series_key",
    "mart_company_yearly": "SELECT * FROM mart_company_yearly ORDER BY fiscal_year, ticker",
    "mart_macro_monthly": "SELECT * FROM mart_macro_monthly ORDER BY observation_date",
    "mart_company_economic_context": "SELECT * FROM mart_company_economic_context ORDER BY fiscal_year, ticker",
}


def _build_date_dimension(connection: sqlite3.Connection) -> pd.DataFrame:
    boundaries = query(
        connection,
        """
        SELECT MIN(d) AS min_date, MAX(d) AS max_date
        FROM (
            SELECT period_end AS d FROM fact_financial_metric
            UNION ALL
            SELECT observation_date AS d FROM fact_macro_indicator
        )
        WHERE d IS NOT NULL
        """,
    )
    min_date = boundaries.loc[0, "min_date"] if not boundaries.empty else None
    max_date = boundaries.loc[0, "max_date"] if not boundaries.empty else None

    if not min_date or not max_date:
        today = date.today()
        min_date = f"{today.year}-01-01"
        max_date = f"{today.year}-12-31"

    dates = pd.date_range(min_date, max_date, freq="D")
    return pd.DataFrame(
        {
            "date": dates.date.astype(str),
            "year": dates.year,
            "quarter": "Q" + dates.quarter.astype(str),
            "month_number": dates.month,
            "month_name": dates.month_name(),
            "year_month": dates.strftime("%Y-%m"),
        }
    )


def export_powerbi(connection: sqlite3.Connection, output_dir: str | Path) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for name, sql in EXPORT_QUERIES.items():
        output = destination / f"{name}.csv"
        query(connection, sql).to_csv(output, index=False)
        written.append(output)

    date_output = destination / "dim_date.csv"
    _build_date_dimension(connection).to_csv(date_output, index=False)
    written.append(date_output)
    return written
