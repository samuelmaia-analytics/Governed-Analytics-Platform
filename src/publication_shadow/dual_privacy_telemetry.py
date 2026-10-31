from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import PUBLISHED_MONITORING_DIR
from src.publication_shadow.dual_privacy import DualPrivacyPolicyComparison

DUAL_PRIVACY_POLICY_ID = "publication_gate"
DUAL_PRIVACY_POLICY_VERSION = "v1"
DUAL_PRIVACY_COMPARISON_ID = "inherent_vs_residual_v1"
DEFAULT_DUAL_PRIVACY_TELEMETRY_PATH = (
    PUBLISHED_MONITORING_DIR / "dual_privacy_shadow_comparisons.jsonl"
)


def serialize_dual_privacy_comparison(
    comparison: DualPrivacyPolicyComparison,
    *,
    timestamp_utc: datetime,
) -> dict[str, Any]:
    if timestamp_utc.utcoffset() is None:
        raise ValueError("timestamp_utc must be timezone-aware")
    return {
        "run_id": comparison.run_id,
        "timestamp_utc": timestamp_utc.isoformat(),
        "policy_id": DUAL_PRIVACY_POLICY_ID,
        "policy_version": DUAL_PRIVACY_POLICY_VERSION,
        "comparison_id": DUAL_PRIVACY_COMPARISON_ID,
        "evaluated": comparison.evaluated,
        "inherent_score": comparison.inherent_score,
        "residual_score": comparison.residual_score,
        "inherent_decision": comparison.inherent_decision,
        "residual_decision": comparison.residual_decision,
        "inherent_severity": comparison.inherent_severity,
        "residual_severity": comparison.residual_severity,
        "diverged": comparison.diverged,
        "divergence_type": comparison.divergence_type.value,
        "inherent_reasons": list(comparison.inherent_reasons),
        "residual_reasons": list(comparison.residual_reasons),
        "unavailable_inputs": list(comparison.unavailable_inputs),
    }


def append_dual_privacy_comparison(
    comparison: DualPrivacyPolicyComparison,
    *,
    timestamp_utc: datetime,
    output_path: Path,
) -> Path:
    record = serialize_dual_privacy_comparison(
        comparison, timestamp_utc=timestamp_utc
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return output_path
