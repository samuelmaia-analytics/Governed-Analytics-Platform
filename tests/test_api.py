from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import src.api as api


def _set_bearer_token(
    monkeypatch: pytest.MonkeyPatch,
    *,
    token: str = "test-token",
) -> dict[str, str]:
    monkeypatch.setenv("GAP_API_BEARER_TOKEN", token)
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint() -> None:
    client = TestClient(api.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_governance_status_with_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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

    headers = _set_bearer_token(monkeypatch)
    client = TestClient(api.app)
    response = client.get("/api/v1/governance/status", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["publication_status"] == "Needs Review"
    assert payload["schema_contract_status"] == "failed"
    assert payload["freshness_status"] == "warning"


def test_governance_status_without_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api, "PUBLICATION_DECISION_PATH", tmp_path / "missing.json")
    monkeypatch.setattr(api, "SCHEMA_CONTRACT_RESULTS_PATH", tmp_path / "missing.csv")
    monkeypatch.setattr(
        api, "PUBLISHED_MONITORING_RESULTS_PATH", tmp_path / "missing_monitoring.csv"
    )

    headers = _set_bearer_token(monkeypatch)
    client = TestClient(api.app)
    response = client.get("/api/v1/governance/status", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["publication_status"] == "unknown"
    assert payload["schema_contract_status"] == "unknown"
    assert payload["freshness_status"] == "unknown"


def test_api_requires_bearer_when_environment_and_mode_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("GAP_API_AUTH_MODE", raising=False)
    monkeypatch.delenv("GAP_API_ALLOW_INSECURE_LOCALHOST", raising=False)
    monkeypatch.delenv("GAP_API_BEARER_TOKEN", raising=False)

    client = TestClient(api.app)
    assert client.get("/health").status_code == 200

    response = client.get("/api/v1/governance/status")
    assert response.status_code == 503


@pytest.mark.parametrize("environment", [None, "local", "prod"])
def test_api_environment_never_disables_auth(
    monkeypatch: pytest.MonkeyPatch,
    environment: str | None,
) -> None:
    if environment is None:
        monkeypatch.delenv("ENVIRONMENT", raising=False)
    else:
        monkeypatch.setenv("ENVIRONMENT", environment)

    _set_bearer_token(monkeypatch)

    client = TestClient(api.app)
    response = client.get("/api/v1/governance/status")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_api_auth_mode_off_never_disables_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GAP_API_AUTH_MODE", "off")
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("GAP_API_ALLOW_INSECURE_LOCALHOST", "1")

    _set_bearer_token(monkeypatch)

    client = TestClient(api.app)
    response = client.get("/api/v1/governance/status")
    assert response.status_code == 401


def test_api_returns_503_when_server_token_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GAP_API_BEARER_TOKEN", raising=False)

    client = TestClient(api.app)
    response = client.get(
        "/api/v1/governance/status",
        headers={"Authorization": "Bearer anything"},
    )
    assert response.status_code == 503
    assert "anything" not in response.json().get("detail", "")


def test_api_rejects_missing_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_bearer_token(monkeypatch)

    client = TestClient(api.app)
    response = client.get("/api/v1/governance/status")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_api_rejects_invalid_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_bearer_token(monkeypatch)

    client = TestClient(api.app)
    response = client.get(
        "/api/v1/governance/status",
        headers={"Authorization": "Bearer wrong"},
    )
    assert response.status_code == 403
    assert "test-token" not in response.json().get("detail", "")


def test_api_allows_valid_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    headers = _set_bearer_token(monkeypatch)

    client = TestClient(api.app)
    response = client.get("/api/v1/governance/status", headers=headers)
    assert response.status_code == 200
