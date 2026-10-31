from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

from src import publication_gate as _publication_gate
from src.publication_evidence.models import PublicationEvidence
from src.publication_gate import PublicationReadinessDecision
from src.publication_provenance.models import (
    EvidenceSource,
    ProvenancedPublicationEvidence,
)
from src.publication_provenance.validation import validate_evidence_provenance

CurrentMonitorDecision = Literal["Approved", "Needs Review"]


@dataclass(frozen=True)
class ShadowPublicationEvaluation:
    evaluated: bool
    canonical_decision: PublicationReadinessDecision | None
    current_monitor_decision: CurrentMonitorDecision
    diverged: bool | None
    unavailable_inputs: tuple[str, ...]


def evaluate_publication_shadow(
    evidence: PublicationEvidence,
    *,
    current_monitor_decision: CurrentMonitorDecision,
) -> ShadowPublicationEvaluation:
    quality_score = evidence.quality_score
    privacy_risk_score = evidence.privacy_risk_score
    critical_quality_failures = evidence.critical_quality_failures
    unavailable: list[str] = []
    if quality_score is None:
        unavailable.append("quality_score")
    if privacy_risk_score is None:
        unavailable.append("privacy_risk_score")
    if critical_quality_failures is None:
        unavailable.append("critical_quality_failures")
    if evidence.schema_status not in {"PASS", "FAIL"}:
        unavailable.append("schema_status")
    if evidence.sensitive_data_protected is None:
        unavailable.append("sensitive_data_protected")
    if evidence.freshness_status not in {"fresh", "warning", "stale"}:
        unavailable.append("freshness_status")

    if unavailable:
        return ShadowPublicationEvaluation(
            evaluated=False,
            canonical_decision=None,
            current_monitor_decision=current_monitor_decision,
            diverged=None,
            unavailable_inputs=tuple(unavailable),
        )

    assert quality_score is not None
    assert privacy_risk_score is not None
    assert critical_quality_failures is not None
    schema_status: Literal["passed", "failed"] = (
        "passed" if evidence.schema_status == "PASS" else "failed"
    )
    freshness_status = cast(
        Literal["fresh", "warning", "stale"], evidence.freshness_status
    )
    decision = _publication_gate.evaluate_publication_readiness(
        data_quality_score=quality_score,
        privacy_risk_score=privacy_risk_score,
        critical_rule_failures=critical_quality_failures,
        freshness_status=freshness_status,
        schema_contract_status=schema_status,
        has_sensitive_data_without_protection=(
            not evidence.sensitive_data_protected
        ),
    )
    return ShadowPublicationEvaluation(
        evaluated=True,
        canonical_decision=decision,
        current_monitor_decision=current_monitor_decision,
        diverged=decision.decision != current_monitor_decision,
        unavailable_inputs=(),
    )


def evaluate_provenanced_publication_shadow(
    envelope: ProvenancedPublicationEvidence,
    *,
    required_sources: frozenset[EvidenceSource],
    current_monitor_decision: CurrentMonitorDecision,
) -> ShadowPublicationEvaluation:
    validation = validate_evidence_provenance(envelope, required_sources)
    if not validation.valid:
        return ShadowPublicationEvaluation(
            evaluated=False,
            canonical_decision=None,
            current_monitor_decision=current_monitor_decision,
            diverged=None,
            unavailable_inputs=validation.reasons,
        )
    return evaluate_publication_shadow(
        envelope.evidence,
        current_monitor_decision=current_monitor_decision,
    )
