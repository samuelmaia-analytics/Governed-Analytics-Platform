from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import PUBLISHED_MONITORING_DIR
from src.governance_history_components import decision_writer as _decision_writer
from src.governance_history_components import history_writer as _history_writer
from src.governance_history_components import metrics as _metrics
from src.governance_history_components import pipeline as _pipeline
from src.governance_history_components import snapshot as _snapshot
from src.governance_types import DataQualityResult, FreshnessStatus, PrivacyRiskResult
from src.risk_scoring import calculate_privacy_risk_score

DEFAULT_HISTORY_PATH = PUBLISHED_MONITORING_DIR / "governance_history.csv"
DEFAULT_PUBLICATION_DECISION_PATH = (
    PUBLISHED_MONITORING_DIR / "publication_decision.json"
)


def _compute_warning_and_critical_failures(
    quality_result: DataQualityResult,
) -> tuple[int, int]:
    return _metrics.compute_warning_and_critical_failures(quality_result)


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
    return _pipeline.append_governance_history(
        build_snapshot_fn=lambda: _snapshot.build_snapshot(
            total_rows=total_rows,
            total_columns=total_columns,
            privacy_result=privacy_result,
            quality_result=quality_result,
            publication_status=publication_status,
            dataset_name=dataset_name,
            run_id=run_id,
            freshness_status=freshness_status,
            compute_failures_fn=_compute_warning_and_critical_failures,
            calculate_metrics_fn=_metrics.calculate_snapshot_metrics,
        ),
        write_history_fn=_history_writer.append_history,
        write_decision_fn=save_publication_decision_artifact,
        history_path=history_path,
        publication_decision_path=publication_decision_path,
    )


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
    return _decision_writer.save_publication_decision_artifact(
        dataset_name=dataset_name,
        publication_status=publication_status,
        data_quality_score=data_quality_score,
        privacy_risk_score=privacy_risk_score,
        failed_checks_count=failed_checks_count,
        timestamp_utc=timestamp_utc,
        output_path=output_path,
    )
