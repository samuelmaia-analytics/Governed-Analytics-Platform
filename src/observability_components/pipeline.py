from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from src.observability_components.models import ObservabilityCheck

ResultFn = Callable[
    [str, bool, str, float | str, float | str, str], ObservabilityCheck
]
HistoryCheckFn = Callable[[pd.DataFrame], ObservabilityCheck]


def evaluate_governance_observability(
    *,
    expected_columns: list[str] | set[str],
    observed_columns: list[str] | set[str],
    freshness_status: str,
    history_df: pd.DataFrame,
    result_fn: ResultFn,
    row_count_anomaly_check_fn: HistoryCheckFn,
    null_rate_drift_check_fn: HistoryCheckFn,
    privacy_risk_trend_check_fn: HistoryCheckFn,
    quality_score_trend_check_fn: HistoryCheckFn,
) -> list[ObservabilityCheck]:
    expected = set(expected_columns)
    observed = set(observed_columns)
    schema_missing = sorted(expected.difference(observed))

    return [
        result_fn(
            "freshness_status",
            freshness_status == "fresh",
            "high",
            freshness_status,
            "fresh",
            "Freshness must be fresh for automatic publication approval.",
        ),
        result_fn(
            "schema_drift",
            len(schema_missing) == 0,
            "high",
            len(schema_missing),
            0,
            f"Missing expected columns: {schema_missing if schema_missing else 'none'}.",
        ),
        row_count_anomaly_check_fn(history_df),
        null_rate_drift_check_fn(history_df),
        privacy_risk_trend_check_fn(history_df),
        quality_score_trend_check_fn(history_df),
    ]
