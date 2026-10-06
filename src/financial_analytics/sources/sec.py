from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from financial_analytics.config import Company

SEC_COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def fetch_company_facts(
    company: Company,
    session: requests.Session,
    raw_dir: str | Path,
    timeout: int = 30,
) -> dict[str, Any]:
    if "User-Agent" not in session.headers:
        raise ValueError("SEC requests require a declared User-Agent with contact information.")

    url = SEC_COMPANYFACTS_URL.format(cik=company.cik.zfill(10))
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()

    output_dir = Path(raw_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{company.ticker.lower()}_companyfacts.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
