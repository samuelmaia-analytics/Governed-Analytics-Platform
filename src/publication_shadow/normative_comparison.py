from __future__ import annotations

from dataclasses import dataclass

from src.normative_publication_policy import (
    EvidenceValidationError,
    NormativeDecision,
    NormativeEvidence,
    NormativePublicationPolicy,
    PolicyValidationError,
    evaluate_normative_policy,
)
from src.publication_gate import (
    FreshnessStatus,
    OperationalPublicationGateDecision,
    PublicationReadinessDecision,
    SchemaContractStatus,
    evaluate_operational_publication_gate,
    evaluate_publication_readiness,
)


@dataclass(frozen=True)
class PublicationReadinessEvidence:
    data_quality_score: int
    privacy_risk_score: int
    critical_rule_failures: int
    freshness_status: FreshnessStatus
    schema_contract_status: SchemaContractStatus
    has_sensitive_data_without_protection: bool


@dataclass(frozen=True)
class OperationalGateEvidence:
    total_checks: int
    pass_checks: int
    warn_checks: int
    fail_checks: int
    critical_failures: int
    privacy_failed_checks: int = 0


@dataclass(frozen=True)
class NormativeShadowComparison:
    """Structured comparison between runtime and normative evaluators.

    This object is strictly observational: `shadow_authorizes_publication`
    always remains False.
    """

    normative: NormativeDecision | None
    readiness: PublicationReadinessDecision | None
    operational_gate: OperationalPublicationGateDecision | None

    normative_error: str | None = None
    readiness_error: str | None = None
    operational_gate_error: str | None = None

    divergences: tuple[str, ...] = ()

    @property
    def shadow_authorizes_publication(self) -> bool:
        return False


def compare_normative_shadow(
    *,
    policy: NormativePublicationPolicy,
    normative_evidence: NormativeEvidence,
    readiness_evidence: PublicationReadinessEvidence | None = None,
    operational_gate_evidence: OperationalGateEvidence | None = None,
) -> NormativeShadowComparison:
    divergences: list[str] = []

    readiness: PublicationReadinessDecision | None = None
    readiness_error: str | None = None
    if readiness_evidence is None:
        readiness_error = "unavailable: evidence not provided"
    else:
        try:
            readiness = evaluate_publication_readiness(
                data_quality_score=readiness_evidence.data_quality_score,
                privacy_risk_score=readiness_evidence.privacy_risk_score,
                critical_rule_failures=readiness_evidence.critical_rule_failures,
                freshness_status=readiness_evidence.freshness_status,
                schema_contract_status=readiness_evidence.schema_contract_status,
                has_sensitive_data_without_protection=(
                    readiness_evidence.has_sensitive_data_without_protection
                ),
            )
        except ValueError as exc:
            readiness_error = f"invalid: {exc}"

    operational_gate: OperationalPublicationGateDecision | None = None
    operational_gate_error: str | None = None
    if operational_gate_evidence is None:
        operational_gate_error = "unavailable: evidence not provided"
    else:
        try:
            operational_gate = evaluate_operational_publication_gate(
                total_checks=operational_gate_evidence.total_checks,
                pass_checks=operational_gate_evidence.pass_checks,
                warn_checks=operational_gate_evidence.warn_checks,
                fail_checks=operational_gate_evidence.fail_checks,
                critical_failures=operational_gate_evidence.critical_failures,
                privacy_failed_checks=operational_gate_evidence.privacy_failed_checks,
            )
        except ValueError as exc:
            operational_gate_error = f"invalid: {exc}"

    normative: NormativeDecision | None = None
    normative_error: str | None = None
    try:
        normative = evaluate_normative_policy(policy, normative_evidence)
    except (PolicyValidationError, EvidenceValidationError) as exc:
        normative_error = f"invalid: {exc}"

    if normative_error is not None:
        divergences.append(f"Normative invalid: {normative_error}.")
    if readiness_error is not None:
        divergences.append(f"Readiness unavailable/invalid: {readiness_error}.")
    if operational_gate_error is not None:
        divergences.append(
            f"Operational gate unavailable/invalid: {operational_gate_error}."
        )

    if normative is not None and readiness is not None:
        if normative.authorized and readiness.decision != "Approved":
            divergences.append(
                "Normativa autoriza, mas readiness nao esta Approved "
                f"({readiness.decision})."
            )
        if (not normative.authorized) and readiness.decision == "Approved":
            divergences.append(
                "Readiness esta Approved, mas normativa nao autoriza "
                f"({normative.decision})."
            )

    if normative is not None and operational_gate is not None:
        gate_allows = operational_gate.decision in {
            "APPROVED",
            "APPROVED_WITH_WARNINGS",
        }
        if normative.authorized and not gate_allows:
            divergences.append(
                "Normativa autoriza, mas gate operacional bloqueou "
                f"({operational_gate.decision})."
            )
        if (not normative.authorized) and gate_allows:
            divergences.append(
                "Gate operacional autorizou, mas normativa nao autoriza "
                f"({normative.decision})."
            )

    if readiness is not None and operational_gate is not None:
        gate_allows = operational_gate.decision in {
            "APPROVED",
            "APPROVED_WITH_WARNINGS",
        }
        if readiness.decision == "Approved" and not gate_allows:
            divergences.append(
                "Readiness esta Approved, mas gate operacional bloqueou "
                f"({operational_gate.decision})."
            )
        if readiness.decision == "Blocked" and gate_allows:
            divergences.append(
                "Readiness esta Blocked, mas gate operacional autorizou "
                f"({operational_gate.decision})."
            )

    return NormativeShadowComparison(
        normative=normative,
        readiness=readiness,
        operational_gate=operational_gate,
        normative_error=normative_error,
        readiness_error=readiness_error,
        operational_gate_error=operational_gate_error,
        divergences=tuple(divergences),
    )