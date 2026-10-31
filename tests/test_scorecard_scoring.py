from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.scorecard_components import scoring
from src.scorecard_components.models import ScorecardMetric


@pytest.mark.parametrize(("severity", "weight"), [("high", 3), ("medium", 2), ("low", 1), ("unknown", 2), (None, 2)])
def test_severity_weights(severity: object, weight: int) -> None:
    assert scoring.severity_weight(severity) == weight


def test_only_pass_literal_counts_as_success() -> None:
    frame = pd.DataFrame([
        {"status": "PASS", "severity": "high"},
        {"status": "WARN", "severity": "medium"},
        {"status": "FAIL", "severity": "low"},
        {"status": "other"},
    ])
    assert scoring.score_from_checks(frame) == (37.5, 4, 3)


@pytest.mark.parametrize(("score", "status"), [(95, "healthy"), (94.99, "attention"), (80, "attention"), (79.99, "critical")])
def test_status_boundaries(score: float, status: str) -> None:
    assert scoring.status_from_score(score) == status


def test_build_metrics_reads_sources_in_order_and_skips_invalid_schema_group() -> None:
    paths = [Path(name) for name in ("quality", "business", "schema", "privacy", "monitor")]
    evidence = {
        paths[0]: pd.DataFrame([{"status": "WARN", "severity": "medium"}]),
        paths[1]: pd.DataFrame([{"status": "PASS", "severity": "high"}]),
        paths[2]: pd.DataFrame([{"status": "PASS"}]),
        paths[3]: pd.DataFrame([{"status": "PASS"}]),
        paths[4]: pd.DataFrame([{"status": "PASS", "severity": "low"}]),
    }
    calls: list[Path] = []
    metrics = scoring.build_metrics(
        read_csv_fn=lambda path: calls.append(path) or evidence[path],
        quality_results_path=paths[0], business_rule_results_path=paths[1],
        schema_contract_results_path=paths[2], privacy_results_path=paths[3],
        published_monitoring_results_path=paths[4],
    )
    assert calls == paths
    assert [metric.dimension for metric in metrics] == ["data_quality", "business_rules", "privacy_governance", "published_monitoring"]
    assert metrics[0].failed_checks == 1
    assert metrics[0].score == 0.0


def test_dataset_scorecards_average_dimensions_and_sort_datasets() -> None:
    metrics = [
        ScorecardMetric("b", "one", 100, "healthy", "x", 1, 0),
        ScorecardMetric("a", "one", 100, "healthy", "x", 1, 0),
        ScorecardMetric("a", "two", 50, "critical", "x", 1, 1),
    ]
    cards = scoring.build_dataset_scorecards(metrics)
    assert [(card.dataset_name, card.governance_score, card.status) for card in cards] == [("a", 75.0, "critical"), ("b", 100.0, "healthy")]
