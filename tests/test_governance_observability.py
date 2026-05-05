from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.governance_observability import (
    evaluate_governance_observability,
    load_governance_history,
    save_observability_results,
)


def test_evaluate_governance_observability_with_healthy_signals() -> None:
    history_df = pd.DataFrame(
        {
            "execution_timestamp": ["2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z"],
            "row_count": [1000, 1100],
            "null_rate": [1.0, 1.2],
            "privacy_risk_score": [30, 35],
            "data_quality_score": [95, 92],
        }
    )
    checks = evaluate_governance_observability(
        expected_columns={"a", "b"},
        observed_columns={"a", "b"},
        freshness_status="fresh",
        history_df=history_df,
    )
    assert len(checks) == 6
    assert all(check.status == "PASS" for check in checks)


def test_evaluate_governance_observability_detects_failures() -> None:
    history_df = pd.DataFrame(
        {
            "execution_timestamp": ["2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z"],
            "row_count": [1000, 1700],
            "null_rate": [2.0, 20.5],
            "privacy_risk_score": [20, 50],
            "data_quality_score": [95, 70],
        }
    )
    checks = evaluate_governance_observability(
        expected_columns={"a", "b", "c"},
        observed_columns={"a"},
        freshness_status="stale",
        history_df=history_df,
    )
    failed = {check.check_name for check in checks if check.status == "FAIL"}
    assert "freshness_status" in failed
    assert "schema_drift" in failed
    assert "row_count_anomaly" in failed
    assert "null_rate_drift" in failed
    assert "privacy_risk_trend" in failed
    assert "quality_score_trend" in failed


def test_save_and_load_observability_files(tmp_path: Path) -> None:
    checks = evaluate_governance_observability(
        expected_columns={"x"},
        observed_columns={"x"},
        freshness_status="fresh",
        history_df=pd.DataFrame(),
    )
    output_path = tmp_path / "governance_observability.json"
    save_observability_results(checks, output_path=output_path)
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["total_checks"] == 6
    assert "checks" in payload

    history_path = tmp_path / "governance_history.csv"
    pd.DataFrame({"execution_timestamp": ["2026-01-01T00:00:00Z"]}).to_csv(history_path, index=False)
    loaded = load_governance_history(history_path)
    assert not loaded.empty
