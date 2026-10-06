from __future__ import annotations

from typing import Any

import pandas as pd

from financial_analytics.config import Company, MetricDefinition


def financial_quality_report(
    frame: pd.DataFrame,
    companies: list[Company],
    metrics: list[MetricDefinition],
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    checks: list[dict[str, Any]] = []

    duplicate_count = int(
        frame.duplicated(subset=["company_key", "fiscal_year", "metric_key"]).sum()
        if not frame.empty
        else 0
    )
    checks.append(
        {
            "check": "financial_fact_primary_key_unique",
            "status": "PASS" if duplicate_count == 0 else "FAIL",
            "detail": f"duplicate rows: {duplicate_count}",
        }
    )

    invalid_values = int(frame["value"].isna().sum()) if not frame.empty else 0
    checks.append(
        {
            "check": "financial_values_not_null",
            "status": "PASS" if invalid_values == 0 else "FAIL",
            "detail": f"null values: {invalid_values}",
        }
    )

    metric_key_by_code = {item.metric_code: item.metric_key for item in metrics}
    required_codes = ["revenue", "net_income", "assets"]
    expected_years = set(range(start_year, end_year + 1))

    for company in companies:
        company_rows = frame[frame["company_key"] == company.company_key]
        for code in required_codes:
            metric_key = metric_key_by_code.get(code)
            actual_years = set(
                company_rows.loc[company_rows["metric_key"] == metric_key, "fiscal_year"].tolist()
            )
            missing = sorted(expected_years - actual_years)
            checks.append(
                {
                    "check": f"coverage_{company.ticker}_{code}",
                    "status": "PASS" if not missing else "WARN",
                    "detail": "complete" if not missing else f"missing years: {missing}",
                }
            )

    return pd.DataFrame(checks)


def macro_quality_report(frame: pd.DataFrame) -> pd.DataFrame:
    duplicate_count = int(
        frame.duplicated(subset=["series_key", "observation_date"]).sum()
        if not frame.empty
        else 0
    )
    invalid_values = int(frame["value"].isna().sum()) if not frame.empty else 0

    return pd.DataFrame(
        [
            {
                "check": "macro_fact_primary_key_unique",
                "status": "PASS" if duplicate_count == 0 else "FAIL",
                "detail": f"duplicate rows: {duplicate_count}",
            },
            {
                "check": "macro_values_not_null",
                "status": "PASS" if invalid_values == 0 else "FAIL",
                "detail": f"null values: {invalid_values}",
            },
        ]
    )
