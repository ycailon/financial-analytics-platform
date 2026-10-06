import pandas as pd

from financial_analytics.config import Company, MetricDefinition
from financial_analytics.quality import financial_quality_report, macro_quality_report


def test_quality_flags_duplicate_financial_rows():
    company = Company(1, "1", "TEST", "Test", "Technology")
    metric = MetricDefinition(1, "revenue", "Revenue", "Income", "USD", "duration", ("Revenue",))
    frame = pd.DataFrame(
        [
            {"company_key": 1, "fiscal_year": 2024, "metric_key": 1, "value": 10.0},
            {"company_key": 1, "fiscal_year": 2024, "metric_key": 1, "value": 10.0},
        ]
    )

    report = financial_quality_report(frame, [company], [metric], 2024, 2024)
    row = report[report["check"] == "financial_fact_primary_key_unique"].iloc[0]

    assert row["status"] == "FAIL"


def test_macro_quality_passes_unique_rows():
    frame = pd.DataFrame(
        [
            {"series_key": 1, "observation_date": "2025-01-01", "value": 100.0},
            {"series_key": 1, "observation_date": "2025-02-01", "value": 101.0},
        ]
    )

    report = macro_quality_report(frame)
    assert set(report["status"]) == {"PASS"}
