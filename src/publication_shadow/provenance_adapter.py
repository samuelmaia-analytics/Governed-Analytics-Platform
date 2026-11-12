from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.publication_provenance.models import EvidenceProvenance
from src.publication_shadow.traceability import (
    ShadowEvaluatorName,
    ShadowEvidenceContext,
)

_ALLOWED_EVALUATORS: set[str] = {"normative", "readiness", "operational_gate"}

@dataclass(frozen=True)
class EvaluatorProvenanceMetadata:
    """Explicit provenance metadata provided for a single evaluator.

    This is an observability-only adapter input. It must not infer provenance
    for other evaluators from a single envelope.
    """

    evaluator_name: ShadowEvaluatorName
    provenance: EvidenceProvenance | None = None
    policy_fingerprint: str | None = None
    evidence_origin: str | None = None


@dataclass(frozen=True)
class ShadowProvenanceContexts:
    """Traceability contexts produced from explicit provenance metadata."""

    normative: ShadowEvidenceContext | None
    readiness: ShadowEvidenceContext | None
    operational_gate: ShadowEvidenceContext | None

    @property
    def authorizes_publication(self) -> bool:
        return False

    def as_tuple(self) -> tuple[ShadowEvidenceContext | None, ...]:
        return (self.normative, self.readiness, self.operational_gate)


def _normalize_non_empty(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Expected string identifier")
    stripped = value.strip()
    return stripped if stripped else None


def _require_valid_identifier(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    normalized = _normalize_non_empty(value)
    if normalized is None:
        raise ValueError(f"{field_name} must not be empty or whitespace")
    return normalized


def _build_context(meta: EvaluatorProvenanceMetadata) -> ShadowEvidenceContext | None:
    provenance = meta.provenance

    dataset_id: str | None = None
    execution_id: str | None = None
    if provenance is not None:
        dataset_id = _require_valid_identifier(
            provenance.dataset_name, field_name="dataset_name"
        )
        execution_id = _require_valid_identifier(provenance.run_id, field_name="run_id")

    evidence_origin = _normalize_non_empty(meta.evidence_origin)
    policy_fingerprint = _normalize_non_empty(meta.policy_fingerprint)

    if provenance is None and evidence_origin is None and policy_fingerprint is None:
        return None

    return ShadowEvidenceContext(
        evaluator_name=meta.evaluator_name,
        dataset_id=dataset_id,
        execution_id=execution_id,
        policy_fingerprint=policy_fingerprint,
        evidence_origin=evidence_origin,
    )


def adapt_explicit_provenance_to_shadow_contexts(
    items: Iterable[EvaluatorProvenanceMetadata],
) -> ShadowProvenanceContexts:
    """Convert explicit per-evaluator provenance metadata into traceability contexts.

    Fail-safe rules:
    - Only uses per-evaluator inputs; no cross-evaluator inference.
    - Rejects duplicate evaluator entries.
    - Rejects whitespace-only dataset_name/run_id when explicitly provided.
    """

    by_name: dict[ShadowEvaluatorName, EvaluatorProvenanceMetadata] = {}
    for item in items:
        if item.evaluator_name not in _ALLOWED_EVALUATORS:
            raise ValueError(
                "Unknown evaluator_name. Expected one of: "
                + ", ".join(sorted(_ALLOWED_EVALUATORS))
                + "."
            )
        if item.evaluator_name in by_name:
            raise ValueError(
                "Duplicate evaluator_name provided: " + repr(item.evaluator_name)
            )
        by_name[item.evaluator_name] = item

    normative = _build_context(
        by_name.get(
            "normative", EvaluatorProvenanceMetadata(evaluator_name="normative")
        )
    )
    readiness = _build_context(
        by_name.get(
            "readiness", EvaluatorProvenanceMetadata(evaluator_name="readiness")
        )
    )
    operational_gate = _build_context(
        by_name.get(
            "operational_gate",
            EvaluatorProvenanceMetadata(evaluator_name="operational_gate"),
        )
    )

    return ShadowProvenanceContexts(
        normative=normative,
        readiness=readiness,
        operational_gate=operational_gate,
    )
