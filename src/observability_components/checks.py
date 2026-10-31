from __future__ import annotations

import pandas as pd

from src.observability_components.models import ObservabilityCheck


def result(
    check_name: str,
    passed: bool,
    severity: str,
    metric_value: float | str,
    threshold: float | str,
    details: str,
) -> ObservabilityCheck:
    return ObservabilityCheck(
        check_name=check_name,
        status="PASS" if passed else "FAIL",
        severity=severity,
        metric_value=metric_value,
        threshold=threshold,
        details=details,
    )


def row_count_anomaly_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    if "row_count" not in history_df.columns or len(history_df) < 2:
        return result(
            "row_count_anomaly",
            True,
            "low",
            "insufficient_history",
            30.0,
            "At least two history points are required for row-count drift evaluation.",
        )
    series = pd.to_numeric(history_df["row_count"], errors="coerce").dropna()
    if len(series) < 2:
        return result(
            "row_count_anomaly",
            True,
            "low",
            "insufficient_history",
            30.0,
            "No numeric history available.",
        )
    latest = float(series.iloc[-1])
    baseline = float(series.iloc[:-1].median()) if len(series) > 1 else latest
    if baseline == 0:
        pct = 0.0 if latest == 0 else 100.0
    else:
        pct = abs((latest - baseline) / baseline) * 100
    return result(
        "row_count_anomaly",
        pct <= 30.0,
        "medium",
        round(pct, 2),
        30.0,
        f"Latest row count variation vs median baseline: {pct:.2f}%.",
    )


def null_rate_drift_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    if "null_rate" not in history_df.columns or len(history_df) < 2:
        return result(
            "null_rate_drift",
            True,
            "low",
            "insufficient_history",
            10.0,
            "No null-rate drift history available.",
        )
    series = pd.to_numeric(history_df["null_rate"], errors="coerce").dropna()
    if len(series) < 2:
        return result(
            "null_rate_drift",
            True,
            "low",
            "insufficient_history",
            10.0,
            "Insufficient numeric null-rate history.",
        )
    latest = float(series.iloc[-1])
    baseline = float(series.iloc[:-1].median())
    drift_pp = latest - baseline
    return result(
        "null_rate_drift",
        drift_pp <= 10.0,
        "medium",
        round(drift_pp, 4),
        10.0,
        f"Null-rate drift in percentage points relative to baseline: {drift_pp:.4f}.",
    )


def privacy_risk_trend_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    if "privacy_risk_score" not in history_df.columns or len(history_df) < 2:
        return result(
            "privacy_risk_trend",
            True,
            "low",
            "insufficient_history",
            15.0,
            "No privacy-risk trend history available.",
        )
    series = pd.to_numeric(
        history_df["privacy_risk_score"], errors="coerce"
    ).dropna()
    if len(series) < 2:
        return result(
            "privacy_risk_trend",
            True,
            "low",
            "insufficient_history",
            15.0,
            "Insufficient numeric risk history.",
        )
    increase = float(series.iloc[-1] - series.iloc[-2])
    return result(
        "privacy_risk_trend",
        increase <= 15.0,
        "high",
        round(increase, 2),
        15.0,
        f"Latest privacy-risk score delta: {increase:.2f}.",
    )


def quality_score_trend_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    if "data_quality_score" not in history_df.columns or len(history_df) < 2:
        return result(
            "quality_score_trend",
            True,
            "low",
            "insufficient_history",
            -10.0,
            "No quality-score trend history available.",
        )
    series = pd.to_numeric(
        history_df["data_quality_score"], errors="coerce"
    ).dropna()
    if len(series) < 2:
        return result(
            "quality_score_trend",
            True,
            "low",
            "insufficient_history",
            -10.0,
            "Insufficient numeric quality history.",
        )
    delta = float(series.iloc[-1] - series.iloc[-2])
    return result(
        "quality_score_trend",
        delta >= -10.0,
        "high",
        round(delta, 2),
        -10.0,
        f"Latest quality-score delta: {delta:.2f}.",
    )
