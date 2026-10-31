from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analytics.olist.pipeline import run_build


def test_run_build_preserves_order_identity_and_artifact_paths(tmp_path: Path) -> None:
    fact_table = pd.DataFrame({"order_id": ["o1"]})
    parquet_path = tmp_path / "fact.parquet"
    csv_path = tmp_path / "fact.csv"
    duckdb_path = tmp_path / "fact.duckdb"
    report_path = tmp_path / "fact.md"
    calls: list[str] = []

    def build_fact() -> pd.DataFrame:
        calls.append("build")
        return fact_table

    def save_outputs(df: pd.DataFrame) -> tuple[Path, Path, Path]:
        calls.append("outputs")
        assert df is fact_table
        return parquet_path, csv_path, duckdb_path

    def save_report(df: pd.DataFrame) -> Path:
        calls.append("report")
        assert df is fact_table
        return report_path

    artifacts = run_build(
        build_fact_fn=build_fact,
        save_outputs_fn=save_outputs,
        save_report_fn=save_report,
    )

    assert calls == ["build", "outputs", "report"]
    assert artifacts.fact_table is fact_table
    assert artifacts.parquet_path == parquet_path
    assert artifacts.csv_path == csv_path
    assert artifacts.duckdb_path == duckdb_path
    assert artifacts.report_path == report_path


@pytest.mark.parametrize("failing_stage", ["build", "outputs", "report"])
def test_run_build_propagates_dependency_exceptions(
    failing_stage: str, tmp_path: Path
) -> None:
    fact_table = pd.DataFrame({"order_id": ["o1"]})

    def fail(stage: str) -> None:
        if failing_stage == stage:
            raise RuntimeError(stage)

    def build_fact() -> pd.DataFrame:
        fail("build")
        return fact_table

    def save_outputs(_df: pd.DataFrame) -> tuple[Path, Path, Path]:
        fail("outputs")
        return tmp_path / "fact.parquet", tmp_path / "fact.csv", tmp_path / "fact.duckdb"

    def save_report(_df: pd.DataFrame) -> Path:
        fail("report")
        return tmp_path / "fact.md"

    with pytest.raises(RuntimeError, match=f"^{failing_stage}$"):
        run_build(
            build_fact_fn=build_fact,
            save_outputs_fn=save_outputs,
            save_report_fn=save_report,
        )
