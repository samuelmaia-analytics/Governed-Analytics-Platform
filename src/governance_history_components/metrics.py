from __future__ import annotations

from dataclasses import dataclass

from src.governance_types import DataQualityResult, PrivacyRiskResult


@dataclass(frozen=True)
class SnapshotMetrics:
    failed_rules_count: int
    warning_rules_count: int
    critical_rules_count: int
    data_quality_score: int
    privacy_risk_score: int
    null_rate: float
    duplicate_rate: float


def compute_warning_and_critical_failures(
    quality_result: DataQualityResult,
) -> tuple[int, int]:
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


def calculate_snapshot_metrics(
    *,
    total_rows: int,
    privacy_result: PrivacyRiskResult,
    quality_result: DataQualityResult,
    warning_and_critical_failures: tuple[int, int],
) -> SnapshotMetrics:
    failed_rules_count = int(quality_result["failed_checks_count"])
    warning_rules_count, critical_rules_count = warning_and_critical_failures
    total_rows_value = int(total_rows)
    duplicate_rows_value = int(quality_result.get("duplicate_rows", 0))
    data_quality_score = max(0, 100 - (failed_rules_count * 10))
    privacy_risk_score = int(privacy_result["score"])
    null_rate = 0.0
    null_pct_by_column = quality_result.get("null_pct_by_column", {})
    if isinstance(null_pct_by_column, dict) and null_pct_by_column:
        null_rate = float(
            sum(float(value) for value in null_pct_by_column.values())
            / len(null_pct_by_column)
        )
    duplicate_rate = (
        0.0
        if total_rows_value == 0
        else float((duplicate_rows_value / total_rows_value) * 100)
    )
    return SnapshotMetrics(
        failed_rules_count=failed_rules_count,
        warning_rules_count=warning_rules_count,
        critical_rules_count=critical_rules_count,
        data_quality_score=data_quality_score,
        privacy_risk_score=privacy_risk_score,
        null_rate=round(null_rate, 4),
        duplicate_rate=round(duplicate_rate, 4),
    )

