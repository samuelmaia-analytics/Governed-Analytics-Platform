from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.monitoring_components import outputs
from src.monitoring_components.models import MonitoringCheckResult


def _results() -> list[MonitoringCheckResult]:
    return [
        MonitoringCheckResult("passing", "PASS", 0, 0, "high", "ok"),
        MonitoringCheckResult("failing", "FAIL", 2, 0, "medium", "broken"),
    ]


def test_save_results_preserves_csv_json_schema_and_timestamp(tmp_path: Path) -> None:
    output_dir = tmp_path / "monitoring"
    csv_path = output_dir / "results.csv"
    json_path = output_dir / "results.json"

    returned = outputs.save_results(
        _results(),
        monitoring_dir=output_dir,
        results_path=csv_path,
        summary_path=json_path,
    )
    stored = pd.read_csv(csv_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert returned == (csv_path, json_path)
    assert stored.columns.tolist() == [
        "check_name",
        "status",
        "metric_value",
        "threshold",
        "severity",
        "details",
    ]
    assert payload["total_checks"] == 2
    assert payload["failed_checks"] == 1
    assert payload["generated_at_utc"].endswith("+00:00")
    assert [item["check_name"] for item in payload["results"]] == [
        "passing",
        "failing",
    ]


def test_render_and_save_report_preserve_current_markdown_and_utf8(
    tmp_path: Path,
) -> None:
    report = outputs.render_report(_results())
    report_path = tmp_path / "docs" / "monitoring.md"

    returned = outputs.save_report(
        report, docs_dir=report_path.parent, report_path=report_path
    )

    assert returned == report_path
    assert report_path.read_text(encoding="utf-8") == report
    assert report.startswith("# Monitoramento da Camada Published\n")
    assert "Checks aprovados: **1**" in report
    assert "`failing`: broken Valor observado=2." in report
    assert report.endswith("\n")


def test_save_results_propagates_csv_error(tmp_path: Path, monkeypatch) -> None:
    def fail_csv(*args: object, **kwargs: object) -> None:
        raise OSError("csv unavailable")

    monkeypatch.setattr(pd.DataFrame, "to_csv", fail_csv)
    with pytest.raises(OSError, match="csv unavailable"):
        outputs.save_results(
            _results(),
            monitoring_dir=tmp_path,
            results_path=tmp_path / "results.csv",
            summary_path=tmp_path / "results.json",
        )


def test_save_report_propagates_write_error(tmp_path: Path, monkeypatch) -> None:
    def fail_write(*args: object, **kwargs: object) -> None:
        raise OSError("markdown unavailable")

    monkeypatch.setattr(Path, "write_text", fail_write)
    with pytest.raises(OSError, match="markdown unavailable"):
        outputs.save_report(
            "report", docs_dir=tmp_path, report_path=tmp_path / "report.md"
        )
