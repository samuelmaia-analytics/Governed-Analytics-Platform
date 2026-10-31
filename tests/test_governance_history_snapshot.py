from __future__ import annotations

import uuid

from src.governance_history_components.metrics import SnapshotMetrics
from src.governance_history_components.snapshot import build_snapshot

EXPECTED_COLUMNS = [
    "run_id", "dataset_name", "execution_timestamp", "row_count", "null_rate",
    "duplicate_rate", "freshness_status", "data_quality_score",
    "privacy_risk_score", "publication_status", "failed_rules_count",
    "warning_rules_count", "critical_rules_count", "run_timestamp", "total_rows",
    "total_columns", "privacy_score", "privacy_risk_level", "failed_checks_count",
]


def _build(run_id: str | None) -> dict[str, object]:
    return build_snapshot(
        total_rows=10,
        total_columns=3,
        privacy_result={"score": 40, "risk_level": "medium"},  # type: ignore[arg-type]
        quality_result={"failed_checks_count": 2},  # type: ignore[arg-type]
        publication_status="Needs Review",
        dataset_name="dashboard",
        run_id=run_id,
        freshness_status="warning",
        compute_failures_fn=lambda value: (1, 1),
        calculate_metrics_fn=lambda **kwargs: SnapshotMetrics(2, 1, 1, 80, 40, 5.0, 20.0),
    )


def test_snapshot_schema_order_and_explicit_run_id() -> None:
    snapshot = _build("run-explicit")
    assert list(snapshot) == EXPECTED_COLUMNS
    assert snapshot["run_id"] == "run-explicit"
    assert snapshot["execution_timestamp"] == snapshot["run_timestamp"]
    assert snapshot["row_count"] == snapshot["total_rows"] == 10
    assert snapshot["privacy_risk_score"] == snapshot["privacy_score"] == 40
    assert snapshot["failed_rules_count"] == snapshot["failed_checks_count"] == 2


def test_snapshot_generates_valid_uuid_and_timezone_timestamp() -> None:
    snapshot = _build(None)
    uuid.UUID(str(snapshot["run_id"]))
    assert "+00:00" in str(snapshot["execution_timestamp"])
