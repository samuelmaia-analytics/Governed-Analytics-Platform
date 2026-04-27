from __future__ import annotations

import pandas as pd

from src.data_quality import generate_data_quality_table, run_data_quality_checks


def build_quality_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["C1", "C2", "C2"],
            "revenue": [100.0, -10.0, -10.0],
            "status": ["ok", "ok", "ok"],
            "order_date": ["2026-01-10", None, None],
        }
    )


def test_detects_nulls() -> None:
    results = run_data_quality_checks(build_quality_df())
    assert "order_date" in results["columns_over_30pct_null"]


def test_detects_duplicates() -> None:
    results = run_data_quality_checks(build_quality_df())
    assert results["duplicate_rows"] > 0


def test_detects_constant_columns() -> None:
    results = run_data_quality_checks(build_quality_df())
    assert "status" in results["constant_columns"]


def test_generates_table_with_status_and_severity() -> None:
    table = generate_data_quality_table(build_quality_df())
    assert {"check_name", "status", "severity"}.issubset(set(table.columns))
