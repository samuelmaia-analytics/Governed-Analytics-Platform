from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from src.config import PUBLISHED_MONITORING_DIR
from src.governance_types import DataQualityResult, FreshnessStatus, PrivacyRiskResult
from src.risk_scoring import calculate_privacy_risk_score
from src.utils import ensure_directory

DEFAULT_HISTORY_PATH = PUBLISHED_MONITORING_DIR / "governance_history.csv"
DEFAULT_PUBLICATION_DECISION_PATH = PUBLISHED_MONITORING_DIR / "publication_decision.json"


def _compute_warning_and_critical_failures(quality_result: DataQualityResult) -> tuple[int, int]:
    checks = quality_result.get("checks", [])
    if not isinstance(checks, list):
        return 0, 0
    warning_count = 0
    critical_count = 0
    for check in checks:
        if not isinstance(check, dict):
            continue
        if str(check.get("status", "")).upper() != "FAIL":
            continue
        severity = str(check.get("severity", "medium")).strip().lower()
        if severity in {"high", "critical"}:
            critical_count += 1
        else:
            warning_count += 1
    return warning_count, critical_count


def append_governance_history(
    *,
    total_rows: int,
    total_columns: int,
    privacy_result: PrivacyRiskResult,
    quality_result: DataQualityResult,
    publication_status: str,
    dataset_name: str = "fact_orders_dashboard",
    run_id: str | None = None,
    freshness_status: FreshnessStatus = "unknown",
    history_path: Path = DEFAULT_HISTORY_PATH,
    publication_decision_path: Path = DEFAULT_PUBLICATION_DECISION_PATH,
) -> Path:
    ensure_directory(history_path.parent)
    run_identifier = run_id or str(uuid4())
    execution_timestamp = datetime.now(timezone.utc).isoformat()
    failed_rules_count = int(quality_result["failed_checks_count"])
    warning_rules_count, critical_rules_count = _compute_warning_and_critical_failures(quality_result)
    total_rows_value = int(total_rows)
    duplicate_rows_value = int(quality_result.get("duplicate_rows", 0))
    row_count = total_rows_value
    null_rate = 0.0
    null_pct_by_column = quality_result.get("null_pct_by_column", {})
    if isinstance(null_pct_by_column, dict) and null_pct_by_column:
        null_rate = float(sum(float(value) for value in null_pct_by_column.values()) / len(null_pct_by_column))
    duplicate_rate = 0.0 if total_rows_value == 0 else float((duplicate_rows_value / total_rows_value) * 100)

    row = {
        # New observability fields
        "run_id": run_identifier,
        "dataset_name": dataset_name,
        "execution_timestamp": execution_timestamp,
        "row_count": row_count,
        "null_rate": round(null_rate, 4),
        "duplicate_rate": round(duplicate_rate, 4),
        "freshness_status": freshness_status,
        "data_quality_score": max(0, 100 - (failed_rules_count * 10)),
        "privacy_risk_score": int(privacy_result["score"]),
        "publication_status": publication_status,
        "failed_rules_count": failed_rules_count,
        "warning_rules_count": warning_rules_count,
        "critical_rules_count": critical_rules_count,
        # Backward-compatible legacy fields
        "run_timestamp": execution_timestamp,
        "total_rows": total_rows_value,
        "total_columns": total_columns,
        "privacy_score": int(privacy_result["score"]),
        "privacy_risk_level": privacy_result["risk_level"],
        "failed_checks_count": failed_rules_count,
    }
    row_df = pd.DataFrame([row])
    if history_path.exists():
        existing = pd.read_csv(history_path)
        row_df = pd.concat([existing, row_df], ignore_index=True)
    row_df.to_csv(history_path, index=False)
    save_publication_decision_artifact(
        dataset_name=dataset_name,
        publication_status=publication_status,
        data_quality_score=int(row["data_quality_score"]),
        privacy_risk_score=int(row["privacy_risk_score"]),
        failed_checks_count=failed_rules_count,
        timestamp_utc=execution_timestamp,
        output_path=publication_decision_path,
    )
    return history_path


def append_governance_history_from_dataframes(
    *,
    df: pd.DataFrame,
    classification_df: pd.DataFrame,
    quality_result: DataQualityResult,
    publication_status: str,
    dataset_name: str = "fact_orders_dashboard",
    run_id: str | None = None,
    freshness_status: FreshnessStatus = "unknown",
    history_path: Path = DEFAULT_HISTORY_PATH,
    publication_decision_path: Path = DEFAULT_PUBLICATION_DECISION_PATH,
) -> Path:
    privacy_result = calculate_privacy_risk_score(classification_df, total_rows=len(df))
    return append_governance_history(
        total_rows=int(len(df)),
        total_columns=int(df.shape[1]),
        privacy_result=privacy_result,
        quality_result=quality_result,
        publication_status=publication_status,
        dataset_name=dataset_name,
        run_id=run_id,
        freshness_status=freshness_status,
        history_path=history_path,
        publication_decision_path=publication_decision_path,
    )


def save_publication_decision_artifact(
    *,
    dataset_name: str,
    publication_status: str,
    data_quality_score: int,
    privacy_risk_score: int,
    failed_checks_count: int,
    timestamp_utc: str,
    output_path: Path = DEFAULT_PUBLICATION_DECISION_PATH,
) -> Path:
    ensure_directory(output_path.parent)
    status_normalized = publication_status.strip() if publication_status else "Needs Review"
    if status_normalized == "Approved":
        decision_reason = "All quality and privacy checks are within configured thresholds."
    elif status_normalized == "Blocked":
        decision_reason = "Blocking governance conditions were detected and publication must be stopped."
    else:
        decision_reason = "One or more controls require manual review before publication."
    payload = {
        "dataset": dataset_name,
        "status": status_normalized,
        "quality_score": int(data_quality_score),
        "privacy_risk_score": int(privacy_risk_score),
        "failed_checks": int(failed_checks_count),
        "timestamp_utc": timestamp_utc,
        "decision_reason": decision_reason,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
