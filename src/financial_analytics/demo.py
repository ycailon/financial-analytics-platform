from __future__ import annotations

from datetime import date
from typing import Any

from financial_analytics.config import Company, MacroSeries, MetricDefinition


def make_demo_sec_payload(
    company: Company,
    metrics: list[MetricDefinition],
    start_year: int,
    end_year: int,
) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    company_scale = 1 + company.company_key * 0.16

    for metric in metrics:
        concept = metric.concepts[0]
        records = []
        for year in range(start_year, end_year + 1):
            growth = 1 + (year - start_year) * 0.08
            revenue = 100_000_000_000 * company_scale * growth
            values = {
                "revenue": revenue,
                "operating_income": revenue * (0.18 + company.company_key * 0.005),
                "net_income": revenue * (0.14 + company.company_key * 0.004),
                "operating_cash_flow": revenue * 0.22,
                "capex": revenue * 0.055,
                "assets": revenue * 1.45,
                "liabilities": revenue * 0.82,
                "equity": revenue * 0.63,
            }
            value = values[metric.metric_code]
            record: dict[str, Any] = {
                "end": f"{year}-12-31",
                "val": round(value, 2),
                "accn": f"0000000000-{str(year)[2:]}-000001",
                "fy": year,
                "fp": "FY",
                "form": "10-K",
                "filed": f"{year + 1}-02-15",
            }
            if metric.period_type == "duration":
                record["start"] = f"{year}-01-01"
            records.append(record)

        facts[concept] = {"units": {metric.unit: records}}

    return {
        "cik": int(company.cik),
        "entityName": company.company_name,
        "facts": {"us-gaap": facts},
    }


def make_demo_bls_payload(
    series: list[MacroSeries],
    start_year: int,
    end_year: int,
) -> dict[str, Any]:
    output_series = []
    for definition in series:
        data = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if definition.series_code == "cpi_u":
                    value = 255 + (year - start_year) * 8.2 + month * 0.42
                else:
                    value = 5.2 - (year - start_year) * 0.18 + ((month % 4) - 1.5) * 0.04
                data.append(
                    {
                        "year": str(year),
                        "period": f"M{month:02d}",
                        "periodName": date(year, month, 1).strftime("%B"),
                        "value": f"{value:.3f}",
                        "footnotes": [{}],
                    }
                )
        output_series.append({"seriesID": definition.series_id, "data": data})

    return {
        "status": "REQUEST_SUCCEEDED",
        "responseTime": 1,
        "message": [],
        "Results": {"series": output_series},
    }
