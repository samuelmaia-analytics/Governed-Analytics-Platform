from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import pytest

from src.observability_components.models import ObservabilityCheck
from src.observability_components.pipeline import evaluate_governance_observability


def test_pipeline_preserves_check_order_and_history_identity() -> None:
    history = pd.DataFrame({"row_count": [1, 2]})
    calls: list[str] = []

    def result_fn(
        name: str,
        passed: bool,
        severity: str,
        metric: float | str,
        threshold: float | str,
        details: str,
    ) -> ObservabilityCheck:
        calls.append(name)
        return ObservabilityCheck(
            name, "PASS" if passed else "FAIL", severity, metric, threshold, details
        )

    def history_check(name: str) -> Callable[[pd.DataFrame], ObservabilityCheck]:
        def run(received: pd.DataFrame) -> ObservabilityCheck:
            assert received is history
            calls.append(name)
            return ObservabilityCheck(name, "PASS", "low", 0.0, 0.0, name)

        return run

    results = evaluate_governance_observability(
        expected_columns={"a", "b"},
        observed_columns={"a"},
        freshness_status="stale",
        history_df=history,
        result_fn=result_fn,
        row_count_anomaly_check_fn=history_check("row_count_anomaly"),
        null_rate_drift_check_fn=history_check("null_rate_drift"),
        privacy_risk_trend_check_fn=history_check("privacy_risk_trend"),
        quality_score_trend_check_fn=history_check("quality_score_trend"),
    )

    assert calls == [
        "freshness_status",
        "schema_drift",
        "row_count_anomaly",
        "null_rate_drift",
        "privacy_risk_trend",
        "quality_score_trend",
    ]
    assert [result.check_name for result in results] == calls
    assert results[0].metric_value == "stale"
    assert results[1].metric_value == 1


def test_pipeline_propagates_check_exception_and_stops() -> None:
    later_calls: list[str] = []

    def result_fn(
        name: str,
        _passed: bool,
        _severity: str,
        _metric: float | str,
        _threshold: float | str,
        _details: str,
    ) -> ObservabilityCheck:
        if name == "schema_drift":
            raise RuntimeError("schema check failed")
        return ObservabilityCheck(name, "PASS", "low", 0.0, 0.0, name)

    def later(_history: pd.DataFrame) -> ObservabilityCheck:
        later_calls.append("called")
        return ObservabilityCheck("later", "PASS", "low", 0.0, 0.0, "later")

    with pytest.raises(RuntimeError, match="schema check failed"):
        evaluate_governance_observability(
            expected_columns={"a"},
            observed_columns={"a"},
            freshness_status="fresh",
            history_df=pd.DataFrame(),
            result_fn=result_fn,
            row_count_anomaly_check_fn=later,
            null_rate_drift_check_fn=later,
            privacy_risk_trend_check_fn=later,
            quality_score_trend_check_fn=later,
        )

    assert later_calls == []
