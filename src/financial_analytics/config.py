from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Company:
    company_key: int
    cik: str
    ticker: str
    company_name: str
    sector: str


@dataclass(frozen=True)
class MetricDefinition:
    metric_key: int
    metric_code: str
    metric_name: str
    category: str
    unit: str
    period_type: str
    concepts: tuple[str, ...]


@dataclass(frozen=True)
class MacroSeries:
    series_key: int
    series_id: str
    series_code: str
    series_name: str
    unit: str
    frequency: str


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_companies(path: str | Path) -> list[Company]:
    raw = _load_yaml(path)
    return [Company(**item) for item in raw.get("companies", [])]


def load_metrics(path: str | Path) -> list[MetricDefinition]:
    raw = _load_yaml(path)
    definitions: list[MetricDefinition] = []
    for metric_code, item in raw.get("metrics", {}).items():
        definitions.append(
            MetricDefinition(
                metric_key=int(item["metric_key"]),
                metric_code=metric_code,
                metric_name=str(item["metric_name"]),
                category=str(item["category"]),
                unit=str(item["unit"]),
                period_type=str(item["period_type"]),
                concepts=tuple(str(v) for v in item["concepts"]),
            )
        )
    return definitions


def load_macro_series(path: str | Path) -> list[MacroSeries]:
    raw = _load_yaml(path)
    return [MacroSeries(**item) for item in raw.get("series", [])]
