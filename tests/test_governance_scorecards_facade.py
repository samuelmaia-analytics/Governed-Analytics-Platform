from __future__ import annotations

from pathlib import Path

import src.governance_scorecards as facade
from src.scorecard_components.models import DatasetScorecard, ScorecardMetric


def test_facade_reexports_models_and_public_api() -> None:
    assert facade.ScorecardMetric is ScorecardMetric
    assert facade.DatasetScorecard is DatasetScorecard
    assert all(callable(getattr(facade, name)) for name in ("_severity_weight", "_read_csv", "_score_from_checks", "_status_from_score", "build_metrics", "build_dataset_scorecards", "save_outputs", "render_report", "save_report", "main"))


def test_helpers_and_build_metrics_delegate_dynamically(monkeypatch) -> None:
    observed: dict[str, object] = {}
    monkeypatch.setattr(facade._scoring, "severity_weight", lambda value: 9)
    monkeypatch.setattr(facade._scoring, "build_metrics", lambda **kwargs: observed.update(kwargs) or [])
    assert facade._severity_weight("high") == 9
    assert facade.build_metrics() == []
    assert observed["read_csv_fn"] is facade._read_csv
    assert observed["quality_results_path"] is facade.QUALITY_RESULTS_PATH


def test_output_wrappers_use_monkeypatchable_facade_paths(tmp_path: Path, monkeypatch) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(facade, "PUBLISHED_MONITORING_DIR", tmp_path)
    monkeypatch.setattr(facade, "SCORECARD_CSV_PATH", tmp_path / "cards.csv")
    monkeypatch.setattr(facade, "SCORECARD_JSON_PATH", tmp_path / "cards.json")
    monkeypatch.setattr(facade._outputs, "save_outputs", lambda *args, **kwargs: captured.update(kwargs) or (kwargs["csv_path"], kwargs["json_path"]))
    assert facade.save_outputs([], []) == (tmp_path / "cards.csv", tmp_path / "cards.json")
    assert captured["output_dir"] == tmp_path


def test_main_preserves_historical_monkeypatches_and_order(monkeypatch) -> None:
    calls: list[str] = []
    metrics: list[ScorecardMetric] = []
    cards: list[DatasetScorecard] = []
    monkeypatch.setattr(facade, "configure_logging", lambda: calls.append("logging"))
    monkeypatch.setattr(facade, "build_metrics", lambda: calls.append("metrics") or metrics)
    monkeypatch.setattr(facade, "build_dataset_scorecards", lambda value: calls.append("cards") or cards)
    monkeypatch.setattr(facade, "save_outputs", lambda m, c: calls.append("outputs"))
    monkeypatch.setattr(facade, "save_report", lambda m, c: calls.append("report"))
    facade.main()
    assert calls == ["logging", "metrics", "cards", "outputs", "report"]
