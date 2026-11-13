from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from src.publication_shadow.execution_identity_manifest import (
    ExecutionIdentityManifest,
    IdentityStatus,
    ManifestEvidenceEntry,
)


class ArtifactMutability(StrEnum):
    """Declarative artifact mutability.

    This is metadata provided explicitly by the producer. In v1, it does not
    enable any identity proof; it is used only to keep the classification
    conservative.
    """

    OVERWRITE = "overwrite"
    APPEND_MULTI_RUN = "append_multi_run"
    UNKNOWN = "unknown"


class EvidenceCondition(StrEnum):
    """Declarative condition of the evidence at the time it is reported."""

    PRESENT = "present"
    MISSING = "missing"
    LEGACY = "legacy"
    OVERWRITTEN = "overwritten"
    CONTRADICTORY = "contradictory"


@dataclass(frozen=True)
class ManifestIdentityInput:
    """Explicit identity values provided by the producer.

    This input object is immutable and purely in-memory.
    """

    run_id: str | None = None
    dataset_name: str | None = None


def build_manifest_evidence_entry(
    *,
    evidence_type: str,
    evidence_origin: str | None = None,
    artifact_reference: str | None = None,
    artifact_mutability: ArtifactMutability = ArtifactMutability.UNKNOWN,
    condition: EvidenceCondition = EvidenceCondition.PRESENT,
) -> ManifestEvidenceEntry:
    """Build a single ManifestEvidenceEntry in a deterministic, fail-safe way.

    Fail-safe rules:
    - Never produces IdentityStatus.PROVEN (v1 contract rejects it).
    - A textual artifact_reference is never treated as proof.
    - Runtime validation rejects non-enum values for mutability/condition.

    Mutability semantics:
    - IdentityStatus.OVERWRITTEN_UNVERIFIABLE represents lack of guarantee of
      per-execution stability, not a claim that an overwrite already occurred.
    - Append multi-run JSONL cannot be treated as immutable-per-execution.
    """

    if not isinstance(artifact_mutability, ArtifactMutability):
        raise ValueError("artifact_mutability must be an ArtifactMutability")
    if not isinstance(condition, EvidenceCondition):
        raise ValueError("condition must be an EvidenceCondition")

    normalized_origin = _require_valid_identifier(
        evidence_origin, field_name="evidence_origin"
    )
    normalized_ref = _require_valid_identifier(
        artifact_reference, field_name="artifact_reference"
    )

    identity_status = _classify_identity_status(
        artifact_mutability=artifact_mutability,
        condition=condition,
    )

    # ManifestEvidenceEntry validates evidence_type runtime + strips whitespace.
    return ManifestEvidenceEntry(
        evidence_type=evidence_type,
        evidence_origin=normalized_origin,
        artifact_reference=normalized_ref,
        identity_status=identity_status,
    )


def build_execution_identity_manifest_v1(
    *,
    identity: ManifestIdentityInput,
    entries: Iterable[ManifestEvidenceEntry],
) -> ExecutionIdentityManifest:
    """Build an ExecutionIdentityManifest v1 without recomputing identity.

    This function is a thin wrapper that:
    - Requires whitespace-only identifiers to be rejected (not silently dropped).
    - Delegates duplicate/contradiction validation to the v1 contract.
    """

    run_id = _require_valid_identifier(identity.run_id, field_name="run_id")
    dataset_name = _require_valid_identifier(
        identity.dataset_name, field_name="dataset_name"
    )

    return ExecutionIdentityManifest.from_entries(
        entries,
        run_id=run_id,
        dataset_name=dataset_name,
    )


def _classify_identity_status(
    *,
    artifact_mutability: ArtifactMutability,
    condition: EvidenceCondition,
) -> IdentityStatus:
    """Classify identity status with explicit conservative precedence.

    Precedence (most specific first):
    1) Explicit contradiction is preserved.
    2) Legacy evidence remains not proven.
    3) Explicit overwritten condition remains not proven.
    4) Overwrite strategy lacks per-execution stability by default.
    5) Append multi-run does not prove per-execution identity.
    6) No condition can produce PROVEN (v1).
    """

    if condition == EvidenceCondition.CONTRADICTORY:
        return IdentityStatus.CONTRADICTORY

    if condition == EvidenceCondition.LEGACY:
        return IdentityStatus.LEGACY_UNVERIFIABLE

    if condition == EvidenceCondition.OVERWRITTEN:
        if artifact_mutability == ArtifactMutability.APPEND_MULTI_RUN:
            raise ValueError(
                "append_multi_run artifacts must not be classified as overwritten"
            )
        return IdentityStatus.OVERWRITTEN_UNVERIFIABLE

    if condition == EvidenceCondition.MISSING:
        return IdentityStatus.MISSING

    if artifact_mutability == ArtifactMutability.OVERWRITE:
        return IdentityStatus.OVERWRITTEN_UNVERIFIABLE

    # Append multi-run (e.g. JSONL) does not map cleanly to v1 states; use the
    # most conservative supported status.
    return IdentityStatus.MISSING


def _require_valid_identifier(value: str | None, *, field_name: str) -> str | None:
    """Reject whitespace-only strings instead of silently normalizing to None."""

    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Expected string identifier")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must not be empty or whitespace")
    return stripped
