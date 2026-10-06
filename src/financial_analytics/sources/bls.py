from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from financial_analytics.config import MacroSeries

BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"


def fetch_bls_series(
    series: list[MacroSeries],
    start_year: int,
    end_year: int,
    session: requests.Session,
    raw_dir: str | Path,
    timeout: int = 30,
) -> dict[str, Any]:
    if not series:
        raise ValueError("At least one BLS series is required.")
    if len(series) > 25:
        raise ValueError("Unregistered BLS requests are limited to 25 series per request.")
    if end_year < start_year:
        raise ValueError("end_year must be greater than or equal to start_year.")
    if end_year - start_year > 9:
        raise ValueError("Unregistered BLS requests are limited to a 10-year window.")

    payload = {
        "seriesid": [item.series_id for item in series],
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    response = session.post(BLS_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        messages = "; ".join(data.get("message") or [])
        raise RuntimeError(f"BLS request failed: {messages or 'unknown error'}")

    output_dir = Path(raw_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "bls_macro.json"
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data
