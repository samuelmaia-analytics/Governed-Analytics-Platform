from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.scorecard_components import outputs
from src.scorecard_components.models import DatasetScorecard, ScorecardMetric


def _values() -> tuple[list[ScorecardMetric], list[DatasetScorecard]]:
    return ([ScorecardMetric("dataset", "quality", 95.0, "healthy", r"C:\old\source.csv", 2, 1)], [DatasetScorecard("dataset", 95.0, "healthy")])


def test_outputs_preserve_csv_json_timestamp_and_old_source_path(tmp_path: Path) -> None:
    metrics, cards = _values()
    csv_path, json_path = outputs.save_outputs(metrics, cards, output_dir=tmp_path, csv_path=tmp_path / "cards.csv", json_path=tmp_path / "cards.json")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert pd.read_csv(csv_path).columns.tolist() == ["dataset_name", "dimension", "score", "status", "source", "total_checks", "failed_checks"]
    assert payload["generated_at_utc"].endswith("+00:00")
    assert payload["metrics"][0]["source"] == r"C:\old\source.csv"


def test_report_writer_preserves_utf8_and_configured_path(tmp_path: Path) -> None:
    metrics, cards = _values()
    report = outputs.render_report(metrics, cards)
    path = tmp_path / "governance_scorecards.md"
    assert outputs.save_report(report, docs_dir=tmp_path, report_path=path) == path
    assert path.read_text(encoding="utf-8") == report
    assert "Métricas por Dimensão" in report
    assert "C:/old/source.csv" in report


def test_output_error_is_propagated(tmp_path: Path, monkeypatch) -> None:
    metrics, cards = _values()
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("write failed")))
    with pytest.raises(OSError, match="write failed"):
        outputs.save_outputs(metrics, cards, output_dir=tmp_path, csv_path=tmp_path / "x.csv", json_path=tmp_path / "x.json")
