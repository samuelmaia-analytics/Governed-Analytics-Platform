from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from src.governance_history_components.metrics import SnapshotMetrics
from src.governance_types import DataQualityResult, FreshnessStatus, PrivacyRiskResult


def build_snapshot(
    *,
    total_rows: int,
    total_columns: int,
    privacy_result: PrivacyRiskResult,
    quality_result: DataQualityResult,
    publication_status: str,
    dataset_name: str,
    run_id: str | None,
    freshness_status: FreshnessStatus,
    compute_failures_fn: Callable[[DataQualityResult], tuple[int, int]],
    calculate_metrics_fn: Callable[..., SnapshotMetrics],
) -> dict[str, object]:
    run_identifier = run_id or str(uuid4())
    execution_timestamp = datetime.now(timezone.utc).isoformat()
    total_rows_value = int(total_rows)
    metrics = calculate_metrics_fn(
        total_rows=total_rows_value,
        privacy_result=privacy_result,
        quality_result=quality_result,
        warning_and_critical_failures=compute_failures_fn(quality_result),
    )
    return {
        "run_id": run_identifier,
        "dataset_name": dataset_name,
        "execution_timestamp": execution_timestamp,
        "row_count": total_rows_value,
        "null_rate": metrics.null_rate,
        "duplicate_rate": metrics.duplicate_rate,
        "freshness_status": freshness_status,
        "data_quality_score": metrics.data_quality_score,
        "privacy_risk_score": metrics.privacy_risk_score,
        "publication_status": publication_status,
        "failed_rules_count": metrics.failed_rules_count,
        "warning_rules_count": metrics.warning_rules_count,
        "critical_rules_count": metrics.critical_rules_count,
        "run_timestamp": execution_timestamp,
        "total_rows": total_rows_value,
        "total_columns": total_columns,
        "privacy_score": metrics.privacy_risk_score,
        "privacy_risk_level": privacy_result["risk_level"],
        "failed_checks_count": metrics.failed_rules_count,
    }

