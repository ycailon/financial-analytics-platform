from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from financial_analytics.config import load_companies, load_macro_series, load_metrics
from financial_analytics.pipeline import run_demo, run_live_refresh

app = typer.Typer(help="Build a financial analytics warehouse from SEC and BLS data.")
console = Console()


def _paths(root: Path) -> dict[str, Path]:
    return {
        "companies": root / "config" / "companies.yaml",
        "metrics": root / "config" / "sec_metrics.yaml",
        "macro": root / "config" / "macro_series.yaml",
        "schema": root / "sql" / "schema.sql",
        "marts": root / "sql" / "marts.sql",
    }


def _show_summary(title: str, summary: dict[str, int]) -> None:
    table = Table(title=title)
    table.add_column("Metric")
    table.add_column("Count", justify="right")
    for key, value in summary.items():
        table.add_row(key.replace("_", " ").title(), str(value))
    console.print(table)


@app.command()
def demo(
    root: Annotated[Path, typer.Option("--root")] = Path("."),
    start_year: Annotated[int, typer.Option("--start-year")] = 2021,
    end_year: Annotated[int, typer.Option("--end-year")] = 2025,
) -> None:
    """Run the full pipeline using generated offline demo data."""
    paths = _paths(root)
    summary = run_demo(
        load_companies(paths["companies"]),
        load_metrics(paths["metrics"]),
        load_macro_series(paths["macro"]),
        start_year,
        end_year,
        root / "data" / "warehouse" / "financial_analytics.db",
        paths["schema"],
        paths["marts"],
        root / "output",
    )
    _show_summary("Demo pipeline complete", summary)
    console.print(f"Warehouse: {(root / 'data/warehouse/financial_analytics.db').resolve()}")
    console.print(f"Power BI exports: {(root / 'output/powerbi').resolve()}")


@app.command()
def refresh(
    root: Annotated[Path, typer.Option("--root")] = Path("."),
    start_year: Annotated[int, typer.Option("--start-year")] = date.today().year - 6,
    end_year: Annotated[int, typer.Option("--end-year")] = date.today().year,
) -> None:
    """Fetch public SEC/BLS data and rebuild the warehouse."""
    paths = _paths(root)
    if end_year - start_year > 9:
        raise typer.BadParameter("BLS unregistered access supports at most a 10-year window.")

    summary = run_live_refresh(
        load_companies(paths["companies"]),
        load_metrics(paths["metrics"]),
        load_macro_series(paths["macro"]),
        start_year,
        end_year,
        root / "data" / "raw",
        root / "data" / "warehouse" / "financial_analytics.db",
        paths["schema"],
        paths["marts"],
        root / "output",
    )
    _show_summary("Live refresh complete", summary)


if __name__ == "__main__":
    app()
