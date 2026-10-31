from __future__ import annotations

import json
import uuid
from pathlib import Path

import pandas as pd

import src.governance_history as history


def _privacy_result(score: int = 40) -> dict[str, object]:
    return {"score": score, "risk_level": "medium"}


def _quality_result() -> dict[str, object]:
    return {
        "failed_checks_count": 2,
        "duplicate_rows": 2,
        "null_pct_by_column": {"a": 10.0, "b": 0.0},
        "checks": [
            {"status": "FAIL", "severity": "high"},
            {"status": "FAIL", "severity": "medium"},
            {"status": "WARN", "severity": "critical"},
        ],
    }


def test_history_auto_run_id_metrics_append_and_decision_schema(tmp_path: Path) -> None:
    history_path = tmp_path / "history.csv"
    decision_path = tmp_path / "decision.json"
    for _ in range(2):
        history.append_governance_history(
            total_rows=10,
            total_columns=3,
            privacy_result=_privacy_result(),  # type: ignore[arg-type]
            quality_result=_quality_result(),  # type: ignore[arg-type]
            publication_status="Needs Review",
            freshness_status="warning",
            history_path=history_path,
            publication_decision_path=decision_path,
        )

    stored = pd.read_csv(history_path)
    decision = json.loads(decision_path.read_text(encoding="utf-8"))

    assert len(stored) == 2
    assert stored["run_id"].nunique() == 2
    assert all(uuid.UUID(value) for value in stored["run_id"])
    assert pd.to_datetime(stored["execution_timestamp"], utc=True).notna().all()
    assert stored.loc[0, "data_quality_score"] == 80
    assert stored.loc[0, "privacy_risk_score"] == 40
    assert stored.loc[0, "warning_rules_count"] == 1
    assert stored.loc[0, "critical_rules_count"] == 1
    assert stored.loc[0, "null_rate"] == 5.0
    assert stored.loc[0, "duplicate_rate"] == 20.0
    assert list(decision) == [
        "dataset",
        "status",
        "quality_score",
        "privacy_risk_score",
        "failed_checks",
        "timestamp_utc",
        "decision_reason",
    ]
    assert "run_id" not in decision


def test_history_from_dataframes_calculates_privacy_and_shape(
    tmp_path: Path, monkeypatch
) -> None:
    history_path = tmp_path / "history.csv"
    decision_path = tmp_path / "decision.json"
    observed: dict[str, object] = {}

    def fake_risk(classification_df: pd.DataFrame, total_rows: int):
        observed["classification"] = classification_df
        observed["rows"] = total_rows
        return _privacy_result(22)

    monkeypatch.setattr(history, "calculate_privacy_risk_score", fake_risk)
    frame = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    classification = pd.DataFrame({"column": ["a"]})

    history.append_governance_history_from_dataframes(
        df=frame,
        classification_df=classification,
        quality_result={"failed_checks_count": 0},  # type: ignore[arg-type]
        publication_status="Approved",
        history_path=history_path,
        publication_decision_path=decision_path,
    )

    stored = pd.read_csv(history_path)
    assert observed == {"classification": classification, "rows": 2}
    assert stored.loc[0, "total_rows"] == 2
    assert stored.loc[0, "total_columns"] == 2
    assert stored.loc[0, "privacy_risk_score"] == 22


def test_publication_decision_reasons_and_types_are_stable(tmp_path: Path) -> None:
    expected_reasons = {
        "Approved": "All quality and privacy checks are within configured thresholds.",
        "Blocked": "Blocking governance conditions were detected and publication must be stopped.",
        "Needs Review": "One or more controls require manual review before publication.",
    }
    for status, reason in expected_reasons.items():
        output = tmp_path / f"{status}.json"
        history.save_publication_decision_artifact(
            dataset_name="fact_orders_dashboard",
            publication_status=status,
            data_quality_score=100,
            privacy_risk_score=22,
            failed_checks_count=0,
            timestamp_utc="2026-01-01T00:00:00+00:00",
            output_path=output,
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
        assert payload["decision_reason"] == reason
        assert payload["quality_score"] == 100
        assert payload["privacy_risk_score"] == 22
