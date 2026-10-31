from __future__ import annotations

import pandas as pd
import pytest

from src.observability_components import checks
from src.observability_components.models import ObservabilityCheck


def test_result_builds_the_canonical_frozen_model() -> None:
    result = checks.result("check", False, "high", 2.0, 1.0, "details")

    assert result == ObservabilityCheck("check", "FAIL", "high", 2.0, 1.0, "details")
    with pytest.raises(AttributeError):
        result.status = "PASS"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("check_fn", "column", "threshold"),
    [
        (checks.row_count_anomaly_check, "row_count", 30.0),
        (checks.null_rate_drift_check, "null_rate", 10.0),
        (checks.privacy_risk_trend_check, "privacy_risk_score", 15.0),
        (checks.quality_score_trend_check, "data_quality_score", -10.0),
    ],
)
def test_drift_checks_treat_insufficient_history_as_pass_low(
    check_fn: object, column: str, threshold: float
) -> None:
    result = check_fn(pd.DataFrame({column: [1]}))  # type: ignore[operator]

    assert result.status == "PASS"
    assert result.severity == "low"
    assert result.metric_value == "insufficient_history"
    assert result.threshold == threshold


@pytest.mark.parametrize(
    ("check_fn", "values", "expected_metric", "expected_severity"),
    [
        (checks.row_count_anomaly_check, [100, 130], 30.0, "medium"),
        (checks.null_rate_drift_check, [1.0, 11.0], 10.0, "medium"),
        (checks.privacy_risk_trend_check, [20, 35], 15.0, "high"),
        (checks.quality_score_trend_check, [90, 80], -10.0, "high"),
    ],
)
def test_drift_threshold_boundaries_pass(
    check_fn: object,
    values: list[float],
    expected_metric: float,
    expected_severity: str,
) -> None:
    column = {
        checks.row_count_anomaly_check: "row_count",
        checks.null_rate_drift_check: "null_rate",
        checks.privacy_risk_trend_check: "privacy_risk_score",
        checks.quality_score_trend_check: "data_quality_score",
    }[check_fn]

    result = check_fn(pd.DataFrame({column: values}))  # type: ignore[operator]

    assert result.status == "PASS"
    assert result.severity == expected_severity
    assert result.metric_value == expected_metric


def test_drift_threshold_breaches_fail() -> None:
    history = pd.DataFrame(
        {
            "row_count": [100, 131],
            "null_rate": [1.0, 11.01],
            "privacy_risk_score": [20, 36],
            "data_quality_score": [90, 79],
        }
    )

    results = [
        checks.row_count_anomaly_check(history),
        checks.null_rate_drift_check(history),
        checks.privacy_risk_trend_check(history),
        checks.quality_score_trend_check(history),
    ]

    assert [result.status for result in results] == ["FAIL"] * 4


def test_zero_row_count_baseline_preserves_current_percentage_rule() -> None:
    assert checks.row_count_anomaly_check(pd.DataFrame({"row_count": [0, 0]})).metric_value == 0.0
    result = checks.row_count_anomaly_check(pd.DataFrame({"row_count": [0, 1]}))
    assert result.metric_value == 100.0
    assert result.status == "FAIL"
