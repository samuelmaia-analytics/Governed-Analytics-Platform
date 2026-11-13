from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from src.config import PUBLISHED_MONITORING_DIR
from src.publication_shadow.comparison import PublicationShadowComparison
from src.publication_shadow.execution_identity_manifest import (
    IdentityStatus,
    ManifestEvidenceEntry,
)
from src.publication_shadow.manifest_entry_factory import (
    ArtifactMutability,
    EvidenceCondition,
    build_manifest_evidence_entry,
)

LOGGER = logging.getLogger(__name__)

SHADOW_POLICY_ID = "publication_gate"
SHADOW_POLICY_VERSION = "v1"
HISTORICAL_POLICY_ID = "published_monitoring_binary_v1"
DEFAULT_SHADOW_TELEMETRY_PATH = (
    PUBLISHED_MONITORING_DIR / "publication_shadow_comparisons.jsonl"
)
SHADOW_COMPARISON_EVIDENCE_TYPE = "publication_shadow_comparisons"
SHADOW_COMPARISON_EVIDENCE_ORIGIN = "publication_shadow.telemetry"


def serialize_shadow_comparison(
    comparison: PublicationShadowComparison,
    *,
    timestamp_utc: datetime,
) -> dict[str, Any]:
    if timestamp_utc.utcoffset() is None:
        raise ValueError("timestamp_utc must be timezone-aware")
    return {
        "run_id": comparison.run_id,
        "timestamp_utc": timestamp_utc.isoformat(),
        "policy_id": SHADOW_POLICY_ID,
        "policy_version": SHADOW_POLICY_VERSION,
        "historical_policy_id": HISTORICAL_POLICY_ID,
        "evaluated": comparison.evaluated,
        "historical_decision": comparison.current_monitor_decision,
        "canonical_decision": comparison.canonical_decision,
        "diverged": comparison.diverged,
        "divergence_type": comparison.divergence_type.value,
        "canonical_severity": comparison.canonical_severity,
        "canonical_reasons": list(comparison.canonical_reasons),
        "canonical_required_actions": list(
            comparison.canonical_required_actions
        ),
        "provenance_valid": comparison.provenance_valid,
        "current_sources": [source.value for source in comparison.current_sources],
        "missing_sources": [source.value for source in comparison.missing_sources],
        "foreign_run_sources": [
            source.value for source in comparison.foreign_run_sources
        ],
        "unknown_sources": [source.value for source in comparison.unknown_sources],
        "unavailable_inputs": list(comparison.unavailable_inputs),
    }


def append_shadow_comparison(
    comparison: PublicationShadowComparison,
    *,
    timestamp_utc: datetime,
    output_path: Path,
    capture_manifest_entry_fn: Callable[[ManifestEvidenceEntry], None] | None = None,
) -> Path:
    record = serialize_shadow_comparison(
        comparison, timestamp_utc=timestamp_utc
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    if capture_manifest_entry_fn is not None:
        try:
            entry = build_manifest_evidence_entry(
                evidence_type=SHADOW_COMPARISON_EVIDENCE_TYPE,
                evidence_origin=SHADOW_COMPARISON_EVIDENCE_ORIGIN,
                artifact_reference=str(output_path),
                artifact_mutability=ArtifactMutability.APPEND_MULTI_RUN,
                condition=EvidenceCondition.PRESENT,
            )
            if entry.identity_status == IdentityStatus.PROVEN:
                raise ValueError(
                    "IdentityStatus.PROVEN must not be produced for shadow telemetry"
                )

            capture_manifest_entry_fn(entry)
        except Exception:
            LOGGER.warning(
                "Observational manifest capture failed for shadow telemetry.",
                exc_info=True,
            )
    return output_path
