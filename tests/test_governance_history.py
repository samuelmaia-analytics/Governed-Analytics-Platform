from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.governance_history import append_governance_history


def test_append_governance_history(tmp_path: Path) -> None:
    output = tmp_path / "governance_history.csv"
    decision_output = tmp_path / "publication_decision.json"
    privacy_result = {
        "score": 40,
        "total_score": 40,
        "risk_level": "medium",
        "explanation": "",
        "summary": "",
        "components": {},
        "score_components": {},
        "per_component_points": {},
        "component_explanations": {},
        "publication_recommendation": "needs_review",
        "recommendations": [],
    }
    quality_result = {
        "total_rows": 10,
        "total_columns": 3,
        "null_pct_by_column": {"a": 10.0, "b": 0.0},
        "columns_over_30pct_null": [],
        "duplicate_rows": 2,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [
            {"check_name": "x", "status": "FAIL", "severity": "high"},
            {"check_name": "y", "status": "FAIL", "severity": "medium"},
        ],
        "failed_checks_count": 2,
    }
    append_governance_history(
        total_rows=10,
        total_columns=3,
        privacy_result=privacy_result,
        quality_result=quality_result,
        publication_status="Needs Review",
        dataset_name="fact_orders_dashboard",
        freshness_status="warning",
        history_path=output,
        publication_decision_path=decision_output,
    )
    append_governance_history(
        total_rows=10,
        total_columns=3,
        privacy_result=privacy_result,
        quality_result=quality_result,
        publication_status="Needs Review",
        dataset_name="fact_orders_dashboard",
        freshness_status="warning",
        history_path=output,
        publication_decision_path=decision_output,
    )
    stored = pd.read_csv(output)
    assert len(stored) == 2
    assert "run_id" in stored.columns
    assert "dataset_name" in stored.columns
    assert "execution_timestamp" in stored.columns
    assert "row_count" in stored.columns
    assert "null_rate" in stored.columns
    assert "duplicate_rate" in stored.columns
    assert "freshness_status" in stored.columns
    assert "privacy_risk_score" in stored.columns
    assert "failed_rules_count" in stored.columns
    assert "warning_rules_count" in stored.columns
    assert "critical_rules_count" in stored.columns
    assert stored["dataset_name"].iloc[0] == "fact_orders_dashboard"
    assert stored["freshness_status"].iloc[0] == "warning"
    assert float(stored["duplicate_rate"].iloc[0]) == 20.0
    assert int(stored["critical_rules_count"].iloc[0]) == 1
    assert int(stored["warning_rules_count"].iloc[0]) == 1
    assert "run_timestamp" in stored.columns
    assert decision_output.exists()
    payload = json.loads(decision_output.read_text(encoding="utf-8"))
    assert payload["dataset"] == "fact_orders_dashboard"
    assert payload["status"] == "Needs Review"
    assert payload["failed_checks"] == 2


def test_append_governance_history_defaults_for_optional_fields(tmp_path: Path) -> None:
    output = tmp_path / "governance_history.csv"
    decision_output = tmp_path / "publication_decision.json"
    privacy_result = {
        "score": 20,
        "total_score": 20,
        "risk_level": "low",
        "explanation": "",
        "summary": "",
        "components": {},
        "score_components": {},
        "per_component_points": {},
        "component_explanations": {},
        "publication_recommendation": "approved",
        "recommendations": [],
    }
    quality_result = {
        "total_rows": 5,
        "total_columns": 2,
        "null_pct_by_column": {},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [],
        "failed_checks_count": 0,
    }
    append_governance_history(
        total_rows=5,
        total_columns=2,
        privacy_result=privacy_result,
        quality_result=quality_result,
        publication_status="Approved",
        history_path=output,
        publication_decision_path=decision_output,
    )
    stored = pd.read_csv(output)
    assert stored["dataset_name"].iloc[0] == "fact_orders_dashboard"
    assert stored["freshness_status"].iloc[0] == "unknown"
    assert int(stored["warning_rules_count"].iloc[0]) == 0
    assert int(stored["critical_rules_count"].iloc[0]) == 0
    payload = json.loads(decision_output.read_text(encoding="utf-8"))
    assert payload["status"] == "Approved"
