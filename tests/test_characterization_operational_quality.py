from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd
import pytest

import src.quality as quality


def test_quality_writers_and_markdown_are_isolated(tmp_path: Path, monkeypatch) -> None:
    quality_dir = tmp_path / "quality"
    docs_dir = tmp_path / "docs"
    results_path = quality_dir / "checks.csv"
    report_path = docs_dir / "quality.md"
    monkeypatch.setattr(quality, "QUALITY_DIR", quality_dir)
    monkeypatch.setattr(quality, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(quality, "QUALITY_RESULTS_PATH", results_path)
    monkeypatch.setattr(quality, "QUALITY_REPORT_PATH", report_path)
    result = quality.QualityCheckResult("demo", "WARN", 1.25, 1.0, "medium", "detail")
    df = pd.DataFrame({"value": [1]})

    assert quality.save_quality_results([result]) == results_path
    assert quality.save_quality_report(df, [result]) == report_path
    stored = pd.read_csv(results_path)
    report = report_path.read_text(encoding="utf-8")

    assert stored.columns.tolist() == [
        "check_name",
        "status",
        "metric_value",
        "threshold",
        "severity",
        "details",
    ]
    assert stored.iloc[0].to_dict() == asdict(result)
    assert report == quality.render_quality_report(df, [result])
    assert "# Relatório de Qualidade de Dados" in report
    assert "| `demo` | **WARN** | 1.25 | 1.0 | medium |" in report


def test_quality_writer_errors_are_propagated(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(quality, "QUALITY_DIR", tmp_path)
    monkeypatch.setattr(quality, "QUALITY_RESULTS_PATH", tmp_path / "checks.csv")
    monkeypatch.setattr(
        pd.DataFrame, "to_csv", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("disk"))
    )

    with pytest.raises(OSError, match="disk"):
        quality.save_quality_results(
            [quality.QualityCheckResult("x", "PASS", 0, 0, "low", "ok")]
        )


def test_operational_quality_public_api_remains_importable() -> None:
    assert all(
        callable(api)
        for api in [
            quality.validate_not_empty,
            quality.load_fact_table,
            quality.run_quality_checks,
            quality.save_quality_results,
            quality.render_quality_report,
            quality.save_quality_report,
        ]
    )
