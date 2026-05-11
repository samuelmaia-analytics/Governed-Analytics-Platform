from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import PUBLISHED_MONITORING_DIR
from src.utils import ensure_directory

DEFAULT_GOVERNANCE_HISTORY_PATH = PUBLISHED_MONITORING_DIR / "governance_history.csv"
DEFAULT_OBSERVABILITY_PATH = PUBLISHED_MONITORING_DIR / "governance_observability.json"


@dataclass(frozen=True)
class ObservabilityCheck:
    check_name: str
    status: str
    severity: str
    metric_value: float | str
    threshold: float | str
    details: str


def _result(
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


def _row_count_anomaly_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    if "row_count" not in history_df.columns or len(history_df) < 2:
        return _result(
            "row_count_anomaly",
            True,
            "low",
            "insufficient_history",
            30.0,
            "At least two history points are required for row-count drift evaluation.",
        )
    series = pd.to_numeric(history_df["row_count"], errors="coerce").dropna()
    if len(series) < 2:
        return _result(
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
    return _result(
        "row_count_anomaly",
        pct <= 30.0,
        "medium",
        round(pct, 2),
        30.0,
        f"Latest row count variation vs median baseline: {pct:.2f}%.",
    )


def _null_rate_drift_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    if "null_rate" not in history_df.columns or len(history_df) < 2:
        return _result(
            "null_rate_drift",
            True,
            "low",
            "insufficient_history",
            10.0,
            "No null-rate drift history available.",
        )
    series = pd.to_numeric(history_df["null_rate"], errors="coerce").dropna()
    if len(series) < 2:
        return _result(
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
    return _result(
        "null_rate_drift",
        drift_pp <= 10.0,
        "medium",
        round(drift_pp, 4),
        10.0,
        f"Null-rate drift in percentage points relative to baseline: {drift_pp:.4f}.",
    )


def _privacy_risk_trend_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    if "privacy_risk_score" not in history_df.columns or len(history_df) < 2:
        return _result(
            "privacy_risk_trend",
            True,
            "low",
            "insufficient_history",
            15.0,
            "No privacy-risk trend history available.",
        )
    series = pd.to_numeric(history_df["privacy_risk_score"], errors="coerce").dropna()
    if len(series) < 2:
        return _result(
            "privacy_risk_trend",
            True,
            "low",
            "insufficient_history",
            15.0,
            "Insufficient numeric risk history.",
        )
    increase = float(series.iloc[-1] - series.iloc[-2])
    return _result(
        "privacy_risk_trend",
        increase <= 15.0,
        "high",
        round(increase, 2),
        15.0,
        f"Latest privacy-risk score delta: {increase:.2f}.",
    )


def _quality_score_trend_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    if "data_quality_score" not in history_df.columns or len(history_df) < 2:
        return _result(
            "quality_score_trend",
            True,
            "low",
            "insufficient_history",
            -10.0,
            "No quality-score trend history available.",
        )
    series = pd.to_numeric(history_df["data_quality_score"], errors="coerce").dropna()
    if len(series) < 2:
        return _result(
            "quality_score_trend",
            True,
            "low",
            "insufficient_history",
            -10.0,
            "Insufficient numeric quality history.",
        )
    delta = float(series.iloc[-1] - series.iloc[-2])
    return _result(
        "quality_score_trend",
        delta >= -10.0,
        "high",
        round(delta, 2),
        -10.0,
        f"Latest quality-score delta: {delta:.2f}.",
    )


def evaluate_governance_observability(
    *,
    expected_columns: list[str] | set[str],
    observed_columns: list[str] | set[str],
    freshness_status: str,
    history_df: pd.DataFrame,
) -> list[ObservabilityCheck]:
    expected = set(expected_columns)
    observed = set(observed_columns)
    schema_missing = sorted(expected.difference(observed))

    checks = [
        _result(
            "freshness_status",
            freshness_status == "fresh",
            "high",
            freshness_status,
            "fresh",
            "Freshness must be fresh for automatic publication approval.",
        ),
        _result(
            "schema_drift",
            len(schema_missing) == 0,
            "high",
            len(schema_missing),
            0,
            f"Missing expected columns: {schema_missing if schema_missing else 'none'}.",
        ),
        _row_count_anomaly_check(history_df),
        _null_rate_drift_check(history_df),
        _privacy_risk_trend_check(history_df),
        _quality_score_trend_check(history_df),
    ]
    return checks


def save_observability_results(
    checks: list[ObservabilityCheck],
    *,
    output_path: Path = DEFAULT_OBSERVABILITY_PATH,
) -> Path:
    ensure_directory(output_path.parent)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_checks": len(checks),
        "failed_checks": sum(1 for item in checks if item.status == "FAIL"),
        "checks": [asdict(item) for item in checks],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return output_path


def load_governance_history(
    path: Path = DEFAULT_GOVERNANCE_HISTORY_PATH,
) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    history_df = pd.read_csv(path)
    if "execution_timestamp" in history_df.columns:
        history_df = history_df.sort_values("execution_timestamp")
    return history_df
