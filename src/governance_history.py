from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import PUBLISHED_MONITORING_DIR
from src.governance_types import DataQualityResult, PrivacyRiskResult
from src.utils import ensure_directory

DEFAULT_HISTORY_PATH = PUBLISHED_MONITORING_DIR / "governance_history.csv"


def append_governance_history(
    *,
    total_rows: int,
    total_columns: int,
    privacy_result: PrivacyRiskResult,
    quality_result: DataQualityResult,
    publication_status: str,
    history_path: Path = DEFAULT_HISTORY_PATH,
) -> Path:
    ensure_directory(history_path.parent)
    row = {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_rows": total_rows,
        "total_columns": total_columns,
        "privacy_score": privacy_result["score"],
        "privacy_risk_level": privacy_result["risk_level"],
        "data_quality_score": max(0, 100 - (quality_result["failed_checks_count"] * 10)),
        "failed_checks_count": quality_result["failed_checks_count"],
        "publication_status": publication_status,
    }
    row_df = pd.DataFrame([row])
    if history_path.exists():
        existing = pd.read_csv(history_path)
        row_df = pd.concat([existing, row_df], ignore_index=True)
    row_df.to_csv(history_path, index=False)
    return history_path

