from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

import src.api as api


def test_health_endpoint() -> None:
    client = TestClient(api.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_governance_status_with_artifacts(tmp_path: Path, monkeypatch) -> None:
    decision_path = tmp_path / "publication_decision.json"
    schema_path = tmp_path / "schema_contract_results.csv"
    monitoring_path = tmp_path / "published_layer_monitoring.csv"

    decision_path.write_text(
        json.dumps(
            {
                "dataset": "fact_orders_dashboard",
                "status": "Needs Review",
                "quality_score": 90,
                "privacy_risk_score": 35,
                "failed_checks": 1,
                "timestamp_utc": "2026-05-11T10:00:00+00:00",
                "decision_reason": "manual review",
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {"check_name": "x", "status": "PASS"},
            {"check_name": "y", "status": "FAIL"},
        ]
    ).to_csv(schema_path, index=False)
    pd.DataFrame(
        [
            {
                "check_name": "published_file_freshness_hours",
                "status": "FAIL",
                "metric_value": 40,
                "threshold": 36,
            }
        ]
    ).to_csv(monitoring_path, index=False)

    monkeypatch.setattr(api, "PUBLICATION_DECISION_PATH", decision_path)
    monkeypatch.setattr(api, "SCHEMA_CONTRACT_RESULTS_PATH", schema_path)
    monkeypatch.setattr(api, "PUBLISHED_MONITORING_RESULTS_PATH", monitoring_path)

    client = TestClient(api.app)
    response = client.get("/api/v1/governance/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["publication_status"] == "Needs Review"
    assert payload["schema_contract_status"] == "failed"
    assert payload["freshness_status"] == "warning"


def test_governance_status_without_artifacts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(api, "PUBLICATION_DECISION_PATH", tmp_path / "missing.json")
    monkeypatch.setattr(api, "SCHEMA_CONTRACT_RESULTS_PATH", tmp_path / "missing.csv")
    monkeypatch.setattr(
        api, "PUBLISHED_MONITORING_RESULTS_PATH", tmp_path / "missing_monitoring.csv"
    )

    client = TestClient(api.app)
    response = client.get("/api/v1/governance/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["publication_status"] == "unknown"
    assert payload["schema_contract_status"] == "unknown"
    assert payload["freshness_status"] == "unknown"
