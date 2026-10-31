from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import PUBLISHED_MONITORING_DIR
from src.observability_components import checks as _checks
from src.observability_components import outputs as _outputs
from src.observability_components import pipeline as _pipeline
from src.observability_components import readers as _readers
from src.observability_components.models import ObservabilityCheck
from src.utils import ensure_directory

DEFAULT_GOVERNANCE_HISTORY_PATH = PUBLISHED_MONITORING_DIR / "governance_history.csv"
DEFAULT_OBSERVABILITY_PATH = PUBLISHED_MONITORING_DIR / "governance_observability.json"


def _result(
    check_name: str,
    passed: bool,
    severity: str,
    metric_value: float | str,
    threshold: float | str,
    details: str,
) -> ObservabilityCheck:
    return _checks.result(
        check_name,
        passed,
        severity,
        metric_value,
        threshold,
        details,
    )


def _row_count_anomaly_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    return _checks.row_count_anomaly_check(history_df)


def _null_rate_drift_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    return _checks.null_rate_drift_check(history_df)


def _privacy_risk_trend_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    return _checks.privacy_risk_trend_check(history_df)


def _quality_score_trend_check(history_df: pd.DataFrame) -> ObservabilityCheck:
    return _checks.quality_score_trend_check(history_df)


def evaluate_governance_observability(
    *,
    expected_columns: list[str] | set[str],
    observed_columns: list[str] | set[str],
    freshness_status: str,
    history_df: pd.DataFrame,
) -> list[ObservabilityCheck]:
    return _pipeline.evaluate_governance_observability(
        expected_columns=expected_columns,
        observed_columns=observed_columns,
        freshness_status=freshness_status,
        history_df=history_df,
        result_fn=_result,
        row_count_anomaly_check_fn=_row_count_anomaly_check,
        null_rate_drift_check_fn=_null_rate_drift_check,
        privacy_risk_trend_check_fn=_privacy_risk_trend_check,
        quality_score_trend_check_fn=_quality_score_trend_check,
    )


def save_observability_results(
    checks: list[ObservabilityCheck],
    *,
    output_path: Path = DEFAULT_OBSERVABILITY_PATH,
) -> Path:
    return _outputs.save_observability_results(
        checks,
        output_path=output_path,
        ensure_directory_fn=ensure_directory,
    )


def load_governance_history(
    path: Path = DEFAULT_GOVERNANCE_HISTORY_PATH,
) -> pd.DataFrame:
    return _readers.load_governance_history(path)
