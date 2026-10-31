from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.business_rule_components.models import BusinessRuleResult
from src.business_rule_components.outputs import (
    render_report,
    save_report,
    save_results,
)


def _results() -> list[BusinessRuleResult]:
    return [BusinessRuleResult("rule", "PASS", "high", 1, 0.01, "residual")]


def _contract() -> dict:
    return {"contract_id": "demo", "version": 1, "dataset_name": "fact", "owner": "owner"}


def test_outputs_preserve_csv_schema_markdown_and_utf8(tmp_path: Path) -> None:
    quality_dir = tmp_path / "quality"
    docs_dir = tmp_path / "docs"
    csv_path = quality_dir / "results.csv"
    report_path = docs_dir / "report.md"

    assert save_results(
        _results(), quality_dir=quality_dir, results_path=csv_path
    ) == csv_path
    assert save_report(
        _results(), _contract(), docs_dir=docs_dir, report_path=report_path
    ) == report_path

    assert pd.read_csv(csv_path).columns.tolist() == [
        "rule_id",
        "status",
        "severity",
        "failed_rows",
        "failure_pct",
        "details",
    ]
    assert report_path.read_text(encoding="utf-8") == render_report(
        _results(), _contract()
    )
    assert report_path.read_bytes()[:3] != b"\xef\xbb\xbf"


@pytest.mark.parametrize("target", ["csv", "report"])
def test_output_errors_propagate(tmp_path: Path, target: str) -> None:
    blocked = tmp_path / target
    blocked.mkdir()
    with pytest.raises((IsADirectoryError, PermissionError, OSError)):
        if target == "csv":
            save_results(_results(), quality_dir=tmp_path, results_path=blocked)
        else:
            save_report(
                _results(), _contract(), docs_dir=tmp_path, report_path=blocked
            )
