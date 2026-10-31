from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import pytest

from src.schema_contract_components.models import ContractCheck
from src.schema_contract_components.outputs import (
    render_report,
    save_report,
    save_results,
)


def _checks() -> list[ContractCheck]:
    return [ContractCheck("demo", "curated", "missing_columns", "PASS", "ok")]


def test_outputs_write_exact_schema_and_utf8_markdown(tmp_path: Path) -> None:
    quality_dir = tmp_path / "quality"
    docs_dir = tmp_path / "docs"
    csv_path = quality_dir / "results.csv"
    report_path = docs_dir / "report.md"
    logger = logging.getLogger("schema-contract-output-test")

    assert save_results(
        _checks(), quality_dir=quality_dir, results_path=csv_path, logger=logger
    ) == csv_path
    assert save_report(
        _checks(), docs_dir=docs_dir, report_path=report_path, logger=logger
    ) == report_path

    stored = pd.read_csv(csv_path)
    report_bytes = report_path.read_bytes()
    assert stored.columns.tolist() == [
        "dataset_name",
        "layer",
        "check_name",
        "status",
        "details",
    ]
    assert report_path.read_text(encoding="utf-8") == render_report(_checks())
    assert report_bytes[:3] != b"\xef\xbb\xbf"
    assert "# Relatorio de Contratos de Schema" in report_bytes.decode("utf-8")


@pytest.mark.parametrize("target", ["csv", "report"])
def test_output_errors_are_propagated(tmp_path: Path, target: str) -> None:
    blocked = tmp_path / target
    blocked.mkdir()
    logger = logging.getLogger("schema-contract-output-test")

    with pytest.raises((IsADirectoryError, PermissionError, OSError)):
        if target == "csv":
            save_results(
                _checks(), quality_dir=tmp_path, results_path=blocked, logger=logger
            )
        else:
            save_report(
                _checks(), docs_dir=tmp_path, report_path=blocked, logger=logger
            )
