from __future__ import annotations

from typing import Any

import pandas as pd

from financial_analytics.config import MacroSeries


def transform_bls_response(
    payload: dict[str, Any],
    series_definitions: list[MacroSeries],
) -> pd.DataFrame:
    definitions = {item.series_id: item for item in series_definitions}
    rows: list[dict[str, Any]] = []

    for series in payload.get("Results", {}).get("series", []):
        definition = definitions.get(series.get("seriesID"))
        if definition is None:
            continue

        for item in series.get("data", []):
            period = str(item.get("period", ""))
            if not period.startswith("M") or period == "M13":
                continue

            try:
                month = int(period[1:])
                year = int(item["year"])
                value = float(item["value"])
            except (TypeError, ValueError):
                continue

            rows.append(
                {
                    "series_key": definition.series_key,
                    "observation_date": f"{year:04d}-{month:02d}-01",
                    "value": value,
                }
            )

    return pd.DataFrame(rows, columns=["series_key", "observation_date", "value"])
