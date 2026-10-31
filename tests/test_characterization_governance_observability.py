from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.governance_observability import (
    evaluate_governance_observability,
    save_observability_results,
)

EXPECTED_CHECKS = [
    "freshness_status",
    "schema_drift",
    "row_count_anomaly",
    "null_rate_drift",
    "privacy_risk_trend",
    "quality_score_trend",
]


def test_observability_order_thresholds_and_boundary_passes() -> None:
    history = pd.DataFrame(
        {
            "row_count": [100, 130],
            "null_rate": [1.0, 11.0],
            "privacy_risk_score": [20, 35],
            "data_quality_score": [90, 80],
        }
    )

    checks = evaluate_governance_observability(
        expected_columns={"a"},
        observed_columns={"a"},
        freshness_status="fresh",
        history_df=history,
    )

    assert [check.check_name for check in checks] == EXPECTED_CHECKS
    assert all(check.status == "PASS" for check in checks)
    assert [check.threshold for check in checks] == ["fresh", 0, 30.0, 10.0, 15.0, -10.0]
    assert [check.metric_value for check in checks[2:]] == [30.0, 10.0, 15.0, -10.0]


def test_observability_threshold_breaches_fail() -> None:
    history = pd.DataFrame(
        {
            "row_count": [100, 131],
            "null_rate": [1.0, 11.01],
            "privacy_risk_score": [20, 36],
            "data_quality_score": [90, 79],
        }
    )
    checks = evaluate_governance_observability(
        expected_columns={"a", "b"},
        observed_columns={"a"},
        freshness_status="stale",
        history_df=history,
    )

    assert [check.status for check in checks] == ["FAIL"] * 6


def test_insufficient_history_is_pass_low_and_writer_is_isolated(
    tmp_path: Path,
) -> None:
    checks = evaluate_governance_observability(
        expected_columns={"a"},
        observed_columns={"a"},
        freshness_status="fresh",
        history_df=pd.DataFrame(),
    )
    trend_checks = checks[2:]

    assert all(check.status == "PASS" for check in trend_checks)
    assert all(check.severity == "low" for check in trend_checks)
    assert all(check.metric_value == "insufficient_history" for check in trend_checks)

    output_path = tmp_path / "observability.json"
    save_observability_results(checks, output_path=output_path)
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["total_checks"] == 6
    assert payload["failed_checks"] == 0
    assert payload["checks"] == [asdict(check) for check in checks]
