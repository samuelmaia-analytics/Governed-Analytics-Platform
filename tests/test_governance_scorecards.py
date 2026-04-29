from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src import governance_scorecards as scorecards


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def test_build_metrics_and_dataset_scorecards(tmp_path: Path, monkeypatch) -> None:
    quality_path = tmp_path / "quality" / "fact_orders_enriched_quality_checks.csv"
    business_rules_path = tmp_path / "quality" / "business_rule_results.csv"
    schema_path = tmp_path / "quality" / "schema_contract_results.csv"
    privacy_path = tmp_path / "quality" / "privacy_governance_results.csv"
    monitoring_path = tmp_path / "published" / "monitoring" / "published_layer_monitoring.csv"

    _write_csv(
        quality_path,
        [{"check_name": "q1", "status": "PASS", "severity": "high"}, {"check_name": "q2", "status": "FAIL", "severity": "medium"}],
    )
    _write_csv(
        business_rules_path,
        [{"rule_id": "r1", "status": "PASS", "severity": "high"}, {"rule_id": "r2", "status": "PASS", "severity": "low"}],
    )
    _write_csv(
        schema_path,
        [
            {"dataset_name": "fact_orders_enriched", "status": "PASS"},
            {"dataset_name": "fact_orders_dashboard", "status": "FAIL"},
        ],
    )
    _write_csv(privacy_path, [{"check_name": "p1", "status": "PASS"}, {"check_name": "p2", "status": "PASS"}])
    _write_csv(monitoring_path, [{"check_name": "m1", "status": "PASS", "severity": "high"}])

    monkeypatch.setattr(scorecards, "QUALITY_RESULTS_PATH", quality_path)
    monkeypatch.setattr(scorecards, "BUSINESS_RULE_RESULTS_PATH", business_rules_path)
    monkeypatch.setattr(scorecards, "SCHEMA_CONTRACT_RESULTS_PATH", schema_path)
    monkeypatch.setattr(scorecards, "PRIVACY_RESULTS_PATH", privacy_path)
    monkeypatch.setattr(scorecards, "PUBLISHED_MONITORING_RESULTS_PATH", monitoring_path)

    metrics = scorecards.build_metrics()
    datasets = scorecards.build_dataset_scorecards(metrics)

    assert metrics
    assert any(metric.dataset_name == "fact_orders_enriched" for metric in metrics)
    assert any(metric.dataset_name == "fact_orders_dashboard" for metric in metrics)
    assert any(item.dataset_name == "fact_orders_dashboard" for item in datasets)


def test_save_outputs_and_report(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(scorecards, "PUBLISHED_MONITORING_DIR", tmp_path / "published" / "monitoring")
    monkeypatch.setattr(scorecards, "DOCS_DIR", tmp_path / "docs")
    monkeypatch.setattr(scorecards, "SCORECARD_CSV_PATH", tmp_path / "published" / "monitoring" / "governance_scorecards.csv")
    monkeypatch.setattr(scorecards, "SCORECARD_JSON_PATH", tmp_path / "published" / "monitoring" / "governance_scorecards.json")
    monkeypatch.setattr(scorecards, "REPORT_PATH", tmp_path / "docs" / "governance_scorecards.md")
    metrics = [scorecards.ScorecardMetric("fact_orders_dashboard", "published_monitoring", 100.0, "healthy", "x", 5, 0)]
    dataset_cards = [scorecards.DatasetScorecard("fact_orders_dashboard", 100.0, "healthy")]

    csv_path, json_path = scorecards.save_outputs(metrics, dataset_cards)
    report_path = scorecards.save_report(metrics, dataset_cards)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert csv_path.exists()
    assert report_path.exists()
    assert payload["dataset_scorecards"][0]["dataset_name"] == "fact_orders_dashboard"

