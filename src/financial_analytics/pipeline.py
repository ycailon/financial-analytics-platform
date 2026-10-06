from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from financial_analytics.config import Company, MacroSeries, MetricDefinition
from financial_analytics.demo import make_demo_bls_payload, make_demo_sec_payload
from financial_analytics.export import export_powerbi
from financial_analytics.http import build_session
from financial_analytics.quality import financial_quality_report, macro_quality_report
from financial_analytics.sources.bls import fetch_bls_series
from financial_analytics.sources.sec import fetch_company_facts
from financial_analytics.transform.bls import transform_bls_response
from financial_analytics.transform.sec import transform_company_facts
from financial_analytics.warehouse import connect, execute_sql_file, load_dimensions, replace_fact_table


def build_from_payloads(
    sec_payloads: dict[str, dict],
    bls_payload: dict,
    companies: list[Company],
    metrics: list[MetricDefinition],
    macro_series: list[MacroSeries],
    start_year: int,
    end_year: int,
    warehouse_path: str | Path,
    schema_path: str | Path,
    marts_path: str | Path,
    output_dir: str | Path,
) -> dict[str, int]:
    financial_frames = []
    for company in companies:
        payload = sec_payloads.get(company.ticker)
        if payload is None:
            continue
        financial_frames.append(
            transform_company_facts(payload, company, metrics, start_year, end_year)
        )

    financial = (
        pd.concat(financial_frames, ignore_index=True)
        if financial_frames
        else pd.DataFrame(
            columns=[
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
        )
    )
    macro = transform_bls_response(bls_payload, macro_series)

    connection = connect(warehouse_path)
    try:
        execute_sql_file(connection, schema_path)
        load_dimensions(connection, companies, metrics, macro_series)
        replace_fact_table(connection, "fact_financial_metric", financial)
        replace_fact_table(connection, "fact_macro_indicator", macro)
        execute_sql_file(connection, marts_path)

        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        export_powerbi(connection, destination / "powerbi")

        financial_quality_report(
            financial, companies, metrics, start_year, end_year
        ).to_csv(destination / "financial_quality_report.csv", index=False)
        macro_quality_report(macro).to_csv(destination / "macro_quality_report.csv", index=False)
    finally:
        connection.close()

    summary = {
        "companies_configured": len(companies),
        "companies_loaded": len(sec_payloads),
        "financial_fact_rows": len(financial),
        "macro_fact_rows": len(macro),
    }
    (Path(output_dir) / "pipeline_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def run_demo(
    companies: list[Company],
    metrics: list[MetricDefinition],
    macro_series: list[MacroSeries],
    start_year: int,
    end_year: int,
    warehouse_path: str | Path,
    schema_path: str | Path,
    marts_path: str | Path,
    output_dir: str | Path,
) -> dict[str, int]:
    sec_payloads = {
        company.ticker: make_demo_sec_payload(company, metrics, start_year, end_year)
        for company in companies
    }
    bls_payload = make_demo_bls_payload(macro_series, start_year, end_year)
    return build_from_payloads(
        sec_payloads,
        bls_payload,
        companies,
        metrics,
        macro_series,
        start_year,
        end_year,
        warehouse_path,
        schema_path,
        marts_path,
        output_dir,
    )


def run_live_refresh(
    companies: list[Company],
    metrics: list[MetricDefinition],
    macro_series: list[MacroSeries],
    start_year: int,
    end_year: int,
    raw_dir: str | Path,
    warehouse_path: str | Path,
    schema_path: str | Path,
    marts_path: str | Path,
    output_dir: str | Path,
) -> dict[str, int]:
    load_dotenv()
    user_agent = os.getenv("SEC_USER_AGENT")
    if not user_agent:
        raise ValueError(
            "Set SEC_USER_AGENT before live refresh, for example: "
            "'Your Name your.email@example.com'."
        )

    raw_root = Path(raw_dir)
    sec_session = build_session(user_agent=user_agent)
    public_session = build_session(user_agent="financial-analytics-platform/0.1")

    sec_payloads: dict[str, dict] = {}
    for company in companies:
        sec_payloads[company.ticker] = fetch_company_facts(
            company, sec_session, raw_root / "sec"
        )
        time.sleep(0.15)

    bls_payload = fetch_bls_series(
        macro_series,
        start_year,
        end_year,
        public_session,
        raw_root / "bls",
    )

    return build_from_payloads(
        sec_payloads,
        bls_payload,
        companies,
        metrics,
        macro_series,
        start_year,
        end_year,
        warehouse_path,
        schema_path,
        marts_path,
        output_dir,
    )
