from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any


def append_governance_history(
    *,
    build_snapshot_fn: Callable[[], dict[str, Any]],
    write_history_fn: Callable[..., Path],
    write_decision_fn: Callable[..., Path],
    history_path: Path,
    publication_decision_path: Path,
) -> Path:
    snapshot = build_snapshot_fn()
    written_history_path = write_history_fn(snapshot, history_path=history_path)
    write_decision_fn(
        dataset_name=str(snapshot["dataset_name"]),
        publication_status=str(snapshot["publication_status"]),
        data_quality_score=int(snapshot["data_quality_score"]),
        privacy_risk_score=int(snapshot["privacy_risk_score"]),
        failed_checks_count=int(snapshot["failed_rules_count"]),
        timestamp_utc=str(snapshot["execution_timestamp"]),
        output_path=publication_decision_path,
    )
    return written_history_path
