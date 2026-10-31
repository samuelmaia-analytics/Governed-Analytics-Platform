from __future__ import annotations

import json
from pathlib import Path

from src.utils import ensure_directory


def save_publication_decision_artifact(
    *,
    dataset_name: str,
    publication_status: str,
    data_quality_score: int,
    privacy_risk_score: int,
    failed_checks_count: int,
    timestamp_utc: str,
    output_path: Path,
) -> Path:
    ensure_directory(output_path.parent)
    status_normalized = (
        publication_status.strip() if publication_status else "Needs Review"
    )
    if status_normalized == "Approved":
        decision_reason = (
            "All quality and privacy checks are within configured thresholds."
        )
    elif status_normalized == "Blocked":
        decision_reason = "Blocking governance conditions were detected and publication must be stopped."
    else:
        decision_reason = (
            "One or more controls require manual review before publication."
        )
    payload = {
        "dataset": dataset_name,
        "status": status_normalized,
        "quality_score": int(data_quality_score),
        "privacy_risk_score": int(privacy_risk_score),
        "failed_checks": int(failed_checks_count),
        "timestamp_utc": timestamp_utc,
        "decision_reason": decision_reason,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return output_path
