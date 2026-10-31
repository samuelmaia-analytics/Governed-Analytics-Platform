from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from src.publication_evidence.models import PublicationEvidence
from src.publication_gate import PublicationDecision, PublicationSeverity
from src.publication_provenance.models import EvidenceProvenance
from src.publication_shadow.evaluation import (
    CurrentMonitorDecision,
    ShadowPublicationEvaluation,
    evaluate_publication_shadow,
)


class DualPrivacyDivergenceType(StrEnum):
    AGREEMENT = "agreement"
    RESIDUAL_LESS_RESTRICTIVE = "residual_less_restrictive"
    RESIDUAL_MORE_RESTRICTIVE = "residual_more_restrictive"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class DualPrivacyPolicyComparison:
    """In-memory diagnostic with no publication authority."""

    run_id: str
    evaluated: bool
    inherent_score: int | None
    residual_score: int | None
    inherent_decision: PublicationDecision | None
    residual_decision: PublicationDecision | None
    inherent_severity: PublicationSeverity | None
    residual_severity: PublicationSeverity | None
    diverged: bool | None
    divergence_type: DualPrivacyDivergenceType
    inherent_reasons: tuple[str, ...]
    residual_reasons: tuple[str, ...]
    unavailable_inputs: tuple[str, ...]


@dataclass(frozen=True)
class DualPrivacyShadowEvaluation:
    """Diagnostic comparison; neither branch has publication authority."""

    inherent: ShadowPublicationEvaluation
    residual: ShadowPublicationEvaluation
    inherent_privacy_risk_score: int | None
    residual_privacy_risk_score: int | None


def _unavailable(
    current_monitor_decision: CurrentMonitorDecision, reason: str
) -> ShadowPublicationEvaluation:
    return ShadowPublicationEvaluation(
        evaluated=False,
        canonical_decision=None,
        current_monitor_decision=current_monitor_decision,
        diverged=None,
        unavailable_inputs=(reason,),
    )


def _evaluate_score(
    evidence: PublicationEvidence,
    *,
    score: int | None,
    score_name: str,
    provenance: EvidenceProvenance | None,
    current_run_id: str,
    current_monitor_decision: CurrentMonitorDecision,
) -> ShadowPublicationEvaluation:
    if provenance is None:
        return _unavailable(current_monitor_decision, f"{score_name}: missing provenance")
    if provenance.run_id is None:
        return _unavailable(current_monitor_decision, f"{score_name}: unknown run_id")
    if provenance.run_id != current_run_id:
        return _unavailable(
            current_monitor_decision,
            f"{score_name}: foreign run_id {provenance.run_id!r} "
            f"(current {current_run_id!r})",
        )
    if score is None:
        return _unavailable(current_monitor_decision, f"{score_name}: missing")
    return evaluate_publication_shadow(
        replace(evidence, privacy_risk_score=score),
        current_monitor_decision=current_monitor_decision,
    )


def evaluate_dual_privacy_shadow(
    evidence: PublicationEvidence,
    *,
    inherent_privacy_risk_score: int | None,
    residual_privacy_risk_score: int | None,
    inherent_provenance: EvidenceProvenance | None,
    residual_provenance: EvidenceProvenance | None,
    current_run_id: str,
    current_monitor_decision: CurrentMonitorDecision,
) -> DualPrivacyShadowEvaluation:
    """Evaluate the unchanged policy twice, varying only the privacy score."""

    return DualPrivacyShadowEvaluation(
        inherent=_evaluate_score(
            evidence,
            score=inherent_privacy_risk_score,
            score_name="inherent_privacy_risk_score",
            provenance=inherent_provenance,
            current_run_id=current_run_id,
            current_monitor_decision=current_monitor_decision,
        ),
        residual=_evaluate_score(
            evidence,
            score=residual_privacy_risk_score,
            score_name="residual_privacy_risk_score",
            provenance=residual_provenance,
            current_run_id=current_run_id,
            current_monitor_decision=current_monitor_decision,
        ),
        inherent_privacy_risk_score=inherent_privacy_risk_score,
        residual_privacy_risk_score=residual_privacy_risk_score,
    )


_DECISION_STRICTNESS: dict[PublicationDecision, int] = {
    "Approved": 0,
    "Needs Review": 1,
    "Blocked": 2,
}


def compare_dual_privacy_policy(
    evidence: PublicationEvidence,
    *,
    inherent_privacy_risk_score: int | None,
    residual_privacy_risk_score: int | None,
    inherent_provenance: EvidenceProvenance | None,
    residual_provenance: EvidenceProvenance | None,
    current_run_id: str,
) -> DualPrivacyPolicyComparison:
    """Compare the same policy with inherent and residual privacy scores only."""

    dual = evaluate_dual_privacy_shadow(
        evidence,
        inherent_privacy_risk_score=inherent_privacy_risk_score,
        residual_privacy_risk_score=residual_privacy_risk_score,
        inherent_provenance=inherent_provenance,
        residual_provenance=residual_provenance,
        current_run_id=current_run_id,
        current_monitor_decision="Approved",
    )
    inherent = dual.inherent.canonical_decision
    residual = dual.residual.canonical_decision
    unavailable_inputs = tuple(
        dict.fromkeys(
            (
                *dual.inherent.unavailable_inputs,
                *dual.residual.unavailable_inputs,
            )
        )
    )

    if not dual.inherent.evaluated or not dual.residual.evaluated:
        return DualPrivacyPolicyComparison(
            run_id=current_run_id,
            evaluated=False,
            inherent_score=inherent_privacy_risk_score,
            residual_score=residual_privacy_risk_score,
            inherent_decision=inherent.decision if inherent is not None else None,
            residual_decision=residual.decision if residual is not None else None,
            inherent_severity=inherent.severity if inherent is not None else None,
            residual_severity=residual.severity if residual is not None else None,
            diverged=None,
            divergence_type=DualPrivacyDivergenceType.UNAVAILABLE,
            inherent_reasons=tuple(inherent.reasons) if inherent is not None else (),
            residual_reasons=tuple(residual.reasons) if residual is not None else (),
            unavailable_inputs=unavailable_inputs,
        )

    if inherent is None or residual is None:
        raise ValueError("evaluated dual privacy branches must contain decisions")
    inherent_rank = _DECISION_STRICTNESS[inherent.decision]
    residual_rank = _DECISION_STRICTNESS[residual.decision]
    if residual_rank == inherent_rank:
        divergence_type = DualPrivacyDivergenceType.AGREEMENT
    elif residual_rank < inherent_rank:
        divergence_type = DualPrivacyDivergenceType.RESIDUAL_LESS_RESTRICTIVE
    else:
        divergence_type = DualPrivacyDivergenceType.RESIDUAL_MORE_RESTRICTIVE

    return DualPrivacyPolicyComparison(
        run_id=current_run_id,
        evaluated=True,
        inherent_score=inherent_privacy_risk_score,
        residual_score=residual_privacy_risk_score,
        inherent_decision=inherent.decision,
        residual_decision=residual.decision,
        inherent_severity=inherent.severity,
        residual_severity=residual.severity,
        diverged=divergence_type is not DualPrivacyDivergenceType.AGREEMENT,
        divergence_type=divergence_type,
        inherent_reasons=tuple(inherent.reasons),
        residual_reasons=tuple(residual.reasons),
        unavailable_inputs=(),
    )
