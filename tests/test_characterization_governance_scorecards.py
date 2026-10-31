from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src import governance_scorecards as scorecards


@pytest.mark.parametrize(
    ("severity", "expected_weight"),
    [("high", 3), ("medium", 2), ("low", 1), ("unknown", 2), (None, 2)],
)
def test_severity_weights_are_stable(severity: object, expected_weight: int) -> None:
    assert scorecards._severity_weight(severity) == expected_weight


def test_only_literal_pass_counts_as_success() -> None:
    checks = pd.DataFrame(
        [
            {"status": "PASS", "severity": "high"},
            {"status": "WARN", "severity": "medium"},
            {"status": "FAIL", "severity": "low"},
            {"status": "unexpected"},
        ]
    )

    assert scorecards._score_from_checks(checks) == (37.5, 4, 3)


@pytest.mark.parametrize(
    ("score", "status"),
    [(100.0, "healthy"), (95.0, "healthy"), (94.99, "attention"), (80.0, "attention"), (79.99, "critical")],
)
def test_scorecard_status_boundaries(score: float, status: str) -> None:
    assert scorecards._status_from_score(score) == status


def test_materialized_scorecard_baseline_remains_8_metrics() -> None:
    artifact = pd.read_csv(scorecards.SCORECARD_CSV_PATH)

    assert artifact.shape == (8, 7)
    assert artifact["status"].value_counts().to_dict() == {
        "healthy": 7,
        "critical": 1,
    }
    privacy = artifact.loc[artifact["dimension"] == "privacy_governance"].iloc[0]
    monitoring = artifact.loc[
        artifact["dimension"] == "published_monitoring"
    ].iloc[0]
    assert (privacy["score"], privacy["failed_checks"]) == (25.0, 12)
    assert (monitoring["score"], monitoring["failed_checks"]) == (100.0, 0)
    assert "business_rules" not in artifact["dimension"].tolist()


def test_scorecard_writers_are_isolated(tmp_path: Path, monkeypatch) -> None:
    output_dir = tmp_path / "monitoring"
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(scorecards, "PUBLISHED_MONITORING_DIR", output_dir)
    monkeypatch.setattr(scorecards, "SCORECARD_CSV_PATH", output_dir / "cards.csv")
    monkeypatch.setattr(scorecards, "SCORECARD_JSON_PATH", output_dir / "cards.json")
    monkeypatch.setattr(scorecards, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(scorecards, "REPORT_PATH", docs_dir / "cards.md")
    metrics = [
        scorecards.ScorecardMetric("dataset", "quality", 95.0, "healthy", "x", 2, 1)
    ]
    cards = scorecards.build_dataset_scorecards(metrics)

    csv_path, json_path = scorecards.save_outputs(metrics, cards)
    report_path = scorecards.save_report(metrics, cards)
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert pd.read_csv(csv_path).columns.tolist() == [
        "dataset_name",
        "dimension",
        "score",
        "status",
        "source",
        "total_checks",
        "failed_checks",
    ]
    assert payload["metrics"][0]["score"] == 95.0
    assert payload["dataset_scorecards"][0]["status"] == "healthy"
    assert report_path.is_relative_to(tmp_path)
