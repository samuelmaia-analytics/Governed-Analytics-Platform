"""Minimal orchestration for the Olist analytical build."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd

from src.analytics.olist.outputs import BuildArtifacts

BuildFactFn = Callable[[], pd.DataFrame]
SaveOutputsFn = Callable[[pd.DataFrame], tuple[Path, Path, Path]]
SaveReportFn = Callable[[pd.DataFrame], Path]


def run_build(
    *,
    build_fact_fn: BuildFactFn,
    save_outputs_fn: SaveOutputsFn,
    save_report_fn: SaveReportFn,
) -> BuildArtifacts:
    fact_table = build_fact_fn()
    parquet_path, csv_path, duckdb_path = save_outputs_fn(fact_table)
    report_path = save_report_fn(fact_table)
    return BuildArtifacts(
        fact_table=fact_table,
        parquet_path=parquet_path,
        csv_path=csv_path,
        duckdb_path=duckdb_path,
        report_path=report_path,
    )
