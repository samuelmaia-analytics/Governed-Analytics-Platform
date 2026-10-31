from __future__ import annotations

import pytest

from src.governance_history_components.metrics import (
    calculate_snapshot_metrics,
    compute_warning_and_critical_failures,
)


def test_only_fail_status_contributes_to_warning_and_critical_counts() -> None:
    quality = {
        "checks": [
            {"status": "FAIL", "severity": "high"},
            {"status": "FAIL", "severity": "critical"},
            {"status": "FAIL", "severity": "medium"},
            {"status": "FAIL", "severity": "low"},
            {"status": "WARN", "severity": "critical"},
            {"status": "PASS", "severity": "high"},
        ]
    }
    assert compute_warning_and_critical_failures(quality) == (2, 2)  # type: ignore[arg-type]


def test_invalid_or_missing_checks_produce_zero_counts() -> None:
    assert compute_warning_and_critical_failures({}) == (0, 0)  # type: ignore[arg-type]
    assert compute_warning_and_critical_failures({"checks": "invalid"}) == (0, 0)  # type: ignore[arg-type]


@pytest.mark.parametrize(("failures", "score"), [(0, 100), (2, 80), (10, 0), (20, 0)])
def test_quality_score_has_current_lower_bound(failures: int, score: int) -> None:
    metrics = calculate_snapshot_metrics(
        total_rows=0,
        privacy_result={"score": 22},  # type: ignore[arg-type]
        quality_result={"failed_checks_count": failures},  # type: ignore[arg-type]
        warning_and_critical_failures=(0, 0),
    )
    assert metrics.data_quality_score == score
    assert metrics.privacy_risk_score == 22
    assert metrics.duplicate_rate == 0.0


def test_null_and_duplicate_rates_keep_rounding() -> None:
    metrics = calculate_snapshot_metrics(
        total_rows=3,
        privacy_result={"score": 40},  # type: ignore[arg-type]
        quality_result={
            "failed_checks_count": 1,
            "duplicate_rows": 1,
            "null_pct_by_column": {"a": 1.11111, "b": 2.22222},
        },  # type: ignore[arg-type]
        warning_and_critical_failures=(1, 2),
    )
    assert metrics.null_rate == 1.6667
    assert metrics.duplicate_rate == 33.3333
    assert (metrics.warning_rules_count, metrics.critical_rules_count) == (1, 2)
