from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from src.publication_gate import PublicationDecision, PublicationSeverity
from src.publication_provenance.models import (
    EvidenceSource,
    ProvenanceValidationResult,
)
from src.publication_shadow.evaluation import (
    CurrentMonitorDecision,
    ShadowPublicationEvaluation,
)


class ShadowDivergenceType(StrEnum):
    AGREEMENT = "agreement"
    CANONICAL_STRICTER = "canonical_stricter"
    HISTORICAL_STRICTER = "historical_stricter"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class PublicationShadowComparison:
    run_id: str
    evaluated: bool
    current_monitor_decision: CurrentMonitorDecision
    canonical_decision: PublicationDecision | None
    diverged: bool | None
    divergence_type: ShadowDivergenceType
    canonical_severity: PublicationSeverity | None
    canonical_reasons: tuple[str, ...]
    canonical_required_actions: tuple[str, ...]
    provenance_valid: bool
    current_sources: tuple[EvidenceSource, ...]
    missing_sources: tuple[EvidenceSource, ...]
    foreign_run_sources: tuple[EvidenceSource, ...]
    unknown_sources: tuple[EvidenceSource, ...]
    unavailable_inputs: tuple[str, ...]


@dataclass(frozen=True)
class PublicationShadowTelemetry:
    total: int
    evaluated: int
    unavailable: int
    agreements: int
    canonical_stricter: int
    historical_stricter: int
    divergence_rate: float


_DECISION_STRICTNESS: dict[PublicationDecision, int] = {
    "Approved": 0,
    "Needs Review": 1,
    "Blocked": 2,
}


def _classify_divergence(
    historical: CurrentMonitorDecision,
    canonical: PublicationDecision,
) -> ShadowDivergenceType:
    historical_rank = _DECISION_STRICTNESS[historical]
    canonical_rank = _DECISION_STRICTNESS[canonical]
    if canonical_rank == historical_rank:
        return ShadowDivergenceType.AGREEMENT
    if canonical_rank > historical_rank:
        return ShadowDivergenceType.CANONICAL_STRICTER
    return ShadowDivergenceType.HISTORICAL_STRICTER


def compare_publication_shadow(
    shadow: ShadowPublicationEvaluation,
    provenance: ProvenanceValidationResult,
) -> PublicationShadowComparison:
    if not shadow.evaluated:
        return PublicationShadowComparison(
            run_id=provenance.current_run_id,
            evaluated=False,
            current_monitor_decision=shadow.current_monitor_decision,
            canonical_decision=None,
            diverged=None,
            divergence_type=ShadowDivergenceType.UNAVAILABLE,
            canonical_severity=None,
            canonical_reasons=(),
            canonical_required_actions=(),
            provenance_valid=provenance.valid,
            current_sources=provenance.current_sources,
            missing_sources=provenance.missing_sources,
            foreign_run_sources=provenance.foreign_run_sources,
            unknown_sources=provenance.unknown_sources,
            unavailable_inputs=shadow.unavailable_inputs,
        )

    decision = shadow.canonical_decision
    if decision is None:
        raise ValueError("evaluated shadow must contain a canonical decision")
    divergence_type = _classify_divergence(
        shadow.current_monitor_decision, decision.decision
    )
    return PublicationShadowComparison(
        run_id=provenance.current_run_id,
        evaluated=True,
        current_monitor_decision=shadow.current_monitor_decision,
        canonical_decision=decision.decision,
        diverged=divergence_type is not ShadowDivergenceType.AGREEMENT,
        divergence_type=divergence_type,
        canonical_severity=decision.severity,
        canonical_reasons=tuple(decision.reasons),
        canonical_required_actions=tuple(decision.required_actions),
        provenance_valid=provenance.valid,
        current_sources=provenance.current_sources,
        missing_sources=provenance.missing_sources,
        foreign_run_sources=provenance.foreign_run_sources,
        unknown_sources=provenance.unknown_sources,
        unavailable_inputs=shadow.unavailable_inputs,
    )


def summarize_shadow_comparisons(
    comparisons: Sequence[PublicationShadowComparison],
) -> PublicationShadowTelemetry:
    evaluated = sum(comparison.evaluated for comparison in comparisons)
    agreements = sum(
        comparison.divergence_type is ShadowDivergenceType.AGREEMENT
        for comparison in comparisons
    )
    canonical_stricter = sum(
        comparison.divergence_type is ShadowDivergenceType.CANONICAL_STRICTER
        for comparison in comparisons
    )
    historical_stricter = sum(
        comparison.divergence_type is ShadowDivergenceType.HISTORICAL_STRICTER
        for comparison in comparisons
    )
    divergences = canonical_stricter + historical_stricter
    return PublicationShadowTelemetry(
        total=len(comparisons),
        evaluated=evaluated,
        unavailable=len(comparisons) - evaluated,
        agreements=agreements,
        canonical_stricter=canonical_stricter,
        historical_stricter=historical_stricter,
        divergence_rate=round((divergences / evaluated) * 100, 2) if evaluated else 0.0,
    )
