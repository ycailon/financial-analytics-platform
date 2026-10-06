from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from financial_analytics.config import Company, MetricDefinition

ANNUAL_FORMS = {"10-K", "10-K/A"}


def _duration_is_annual(record: dict[str, Any]) -> bool:
    start = record.get("start")
    end = record.get("end")
    if not start or not end:
        return False
    try:
        days = (date.fromisoformat(end) - date.fromisoformat(start)).days
    except ValueError:
        return False
    return 300 <= days <= 400


def _candidate_records(
    payload: dict[str, Any],
    metric: MetricDefinition,
    start_year: int,
    end_year: int,
) -> list[dict[str, Any]]:
    facts = payload.get("facts", {}).get("us-gaap", {})
    candidates: list[dict[str, Any]] = []

    for priority, concept in enumerate(metric.concepts):
        concept_payload = facts.get(concept, {})
        records = concept_payload.get("units", {}).get(metric.unit, [])
        for record in records:
            fiscal_year = record.get("fy")
            if not isinstance(fiscal_year, int) or not start_year <= fiscal_year <= end_year:
                continue
            if record.get("form") not in ANNUAL_FORMS:
                continue
            period_end = record.get("end")
            if not period_end or str(period_end)[:4] != str(fiscal_year):
                continue
            if record.get("fp") not in {"FY", None}:
                continue
            if metric.period_type == "duration" and not _duration_is_annual(record):
                continue

            candidates.append(
                {
                    **record,
                    "source_concept": concept,
                    "concept_priority": priority,
                }
            )

    return candidates


def transform_company_facts(
    payload: dict[str, Any],
    company: Company,
    metrics: list[MetricDefinition],
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for metric in metrics:
        candidates = _candidate_records(payload, metric, start_year, end_year)
        if not candidates:
            continue

        frame = pd.DataFrame(candidates)
        frame["filed_sort"] = pd.to_datetime(frame["filed"], errors="coerce")
        frame = frame.sort_values(
            ["fy", "concept_priority", "filed_sort"],
            ascending=[True, True, False],
        )
        selected = frame.drop_duplicates(subset=["fy"], keep="first")

        for item in selected.to_dict(orient="records"):
            rows.append(
                {
                    "company_key": company.company_key,
                    "fiscal_year": int(item["fy"]),
                    "period_start": item.get("start"),
                    "period_end": item.get("end"),
                    "metric_key": metric.metric_key,
                    "value": float(item["val"]),
                    "form": item.get("form"),
                    "filed_date": item.get("filed"),
                    "accession_number": item.get("accn"),
                    "source_concept": item.get("source_concept"),
                }
            )

    columns = [
        "company_key",
        "fiscal_year",
        "period_start",
        "period_end",
        "metric_key",
        "value",
        "form",
        "filed_date",
        "accession_number",
        "source_concept",
    ]
    return pd.DataFrame(rows, columns=columns)
