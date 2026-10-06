from pathlib import Path

import sqlite3

from financial_analytics.config import load_companies, load_macro_series, load_metrics
from financial_analytics.pipeline import run_demo


ROOT = Path(__file__).resolve().parents[1]


def test_demo_pipeline_builds_warehouse_and_powerbi_exports(tmp_path: Path):
    companies = load_companies(ROOT / "config" / "companies.yaml")
    metrics = load_metrics(ROOT / "config" / "sec_metrics.yaml")
    macro = load_macro_series(ROOT / "config" / "macro_series.yaml")

    warehouse = tmp_path / "financial.db"
    output = tmp_path / "output"
    summary = run_demo(
        companies,
        metrics,
        macro,
        2021,
        2025,
        warehouse,
        ROOT / "sql" / "schema.sql",
        ROOT / "sql" / "marts.sql",
        output,
    )

    assert summary["companies_loaded"] == 6
    assert summary["financial_fact_rows"] == 240
    assert summary["macro_fact_rows"] == 120
    assert warehouse.exists()
    assert (output / "powerbi" / "mart_company_yearly.csv").exists()
    assert (output / "powerbi" / "mart_macro_monthly.csv").exists()
    assert (output / "financial_quality_report.csv").exists()

    connection = sqlite3.connect(warehouse)
    try:
        yearly_rows = connection.execute("SELECT COUNT(*) FROM mart_company_yearly").fetchone()[0]
        latest_margin = connection.execute(
            """
            SELECT profit_margin
            FROM mart_company_yearly
            WHERE ticker = 'AAPL' AND fiscal_year = 2025
            """
        ).fetchone()[0]
    finally:
        connection.close()

    assert yearly_rows == 30
    assert latest_margin > 0
