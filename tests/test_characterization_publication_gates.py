from __future__ import annotations

from pathlib import Path

import pytest

import app.pages.governance_control_center as control_center
from scripts.run_publication_gate import evaluate_publication_gate
from src.api import _load_publication_decision
from src.publication_gate import evaluate_publication_readiness


def _domain_gate(**overrides: object):
    inputs = {
        "data_quality_score": 100,
        "privacy_risk_score": 0,
        "critical_rule_failures": 0,
        "freshness_status": "fresh",
        "schema_contract_status": "passed",
        "has_sensitive_data_without_protection": False,
    }
    inputs.update(overrides)
    return evaluate_publication_readiness(**inputs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("overrides", "decision", "severity"),
    [
        ({}, "Approved", "Low"),
        ({"data_quality_score": 80}, "Approved", "Low"),
        ({"data_quality_score": 79}, "Needs Review", "Medium"),
        ({"privacy_risk_score": 59}, "Approved", "Low"),
        ({"privacy_risk_score": 60}, "Needs Review", "Medium"),
        ({"privacy_risk_score": 80}, "Needs Review", "High"),
        ({"critical_rule_failures": 1}, "Blocked", "Critical"),
        ({"schema_contract_status": "failed"}, "Blocked", "Critical"),
        ({"has_sensitive_data_without_protection": True}, "Blocked", "Critical"),
    ],
)
def test_domain_publication_gate_boundaries(
    overrides: dict[str, object], decision: str, severity: str
) -> None:
    result = _domain_gate(**overrides)
    assert (result.decision, result.severity) == (decision, severity)


@pytest.mark.parametrize(
    ("quality", "privacy", "critical", "expected"),
    [
        (90, 60, 0, "Approved"),
        (89, 60, 0, "Needs Review"),
        (70, 60, 0, "Needs Review"),
        (69, 60, 0, "Blocked"),
        (90, 61, 0, "Needs Review"),
        (90, 80, 0, "Needs Review"),
        (90, 81, 0, "Blocked"),
        (100, 0, 1, "Blocked"),
    ],
)
def test_cli_publication_gate_boundaries(
    quality: int, privacy: int, critical: int, expected: str
) -> None:
    decision, reason = evaluate_publication_gate(
        quality_score=quality,
        lgpd_risk_score=privacy,
        critical_issues=critical,
    )
    assert decision == expected
    assert reason


def test_streamlit_schema_and_monitoring_missing_or_invalid_are_fail_open(
    tmp_path: Path, monkeypatch
) -> None:
    schema_path = tmp_path / "schema.csv"
    monitoring_path = tmp_path / "monitoring.csv"
    monkeypatch.setattr(control_center, "SCHEMA_CONTRACT_RESULTS_PATH", schema_path)
    monkeypatch.setattr(
        control_center, "PUBLISHED_MONITORING_RESULTS_PATH", monitoring_path
    )

    assert control_center._load_schema_contract_status()[0] == "passed"
    assert control_center._load_freshness_status()[0] == "fresh"

    schema_path.write_text("not,a,valid\ncontract", encoding="utf-8")
    monitoring_path.write_text("not,a,valid\nmonitor", encoding="utf-8")
    assert control_center._load_schema_contract_status()[0] == "passed"
    assert control_center._load_freshness_status()[0] == "fresh"


def test_api_missing_publication_decision_returns_empty_mapping(tmp_path: Path) -> None:
    assert _load_publication_decision(tmp_path / "missing.json") == {}
