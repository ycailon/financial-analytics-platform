from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd

from financial_analytics.config import Company, MacroSeries, MetricDefinition


def connect(path: str | Path) -> sqlite3.Connection:
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def execute_sql_file(connection: sqlite3.Connection, path: str | Path) -> None:
    sql = Path(path).read_text(encoding="utf-8")
    connection.executescript(sql)


def load_dimensions(
    connection: sqlite3.Connection,
    companies: Iterable[Company],
    metrics: Iterable[MetricDefinition],
    macro_series: Iterable[MacroSeries],
) -> None:
    connection.executemany(
        """
        INSERT OR REPLACE INTO dim_company
        (company_key, cik, ticker, company_name, sector)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (item.company_key, item.cik, item.ticker, item.company_name, item.sector)
            for item in companies
        ],
    )
    connection.executemany(
        """
        INSERT OR REPLACE INTO dim_metric
        (metric_key, metric_code, metric_name, category, unit, period_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item.metric_key,
                item.metric_code,
                item.metric_name,
                item.category,
                item.unit,
                item.period_type,
            )
            for item in metrics
        ],
    )
    connection.executemany(
        """
        INSERT OR REPLACE INTO dim_macro_series
        (series_key, series_id, series_code, series_name, unit, frequency)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item.series_key,
                item.series_id,
                item.series_code,
                item.series_name,
                item.unit,
                item.frequency,
            )
            for item in macro_series
        ],
    )
    connection.commit()


def replace_fact_table(connection: sqlite3.Connection, table: str, frame: pd.DataFrame) -> None:
    if table not in {"fact_financial_metric", "fact_macro_indicator"}:
        raise ValueError(f"Unsupported fact table: {table}")

    connection.execute(f"DELETE FROM {table}")
    if frame.empty:
        connection.commit()
        return

    columns = list(frame.columns)
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

    values = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in frame.itertuples(index=False, name=None)
    ]
    connection.executemany(sql, values)
    connection.commit()


def query(connection: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, connection)
