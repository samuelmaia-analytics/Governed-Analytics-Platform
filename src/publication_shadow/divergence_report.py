from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

from src.normative_publication_policy import (
    NormativeEvidence,
    NormativePublicationPolicy,
)
from src.publication_shadow.normative_comparison import (
    NormativeShadowComparison,
    OperationalGateEvidence,
    PublicationReadinessEvidence,
    compare_normative_shadow,
)
from src.publication_shadow.traceability import (
    PolicyIdentityStatus,
    ShadowEvidenceContext,
    TraceabilityAssessment,
    TraceabilityStatus,
    assess_shadow_traceability,
)

ShadowReportClassification = Literal[
    "agreement",
    "divergence",
    "unavailable",
    "invalid",
    "inconclusive",
]


@dataclass(frozen=True)
class ShadowScenario:
    """Single synthetic scenario to evaluate and include in the report."""

    scenario_id: str
    policy: NormativePublicationPolicy
    normative_evidence: NormativeEvidence
    readiness_evidence: PublicationReadinessEvidence | None = None
    operational_gate_evidence: OperationalGateEvidence | None = None

    # Optional: only used for observability/audit of whether the three evaluator
    # outputs can be proven to share the same dataset/execution context.
    traceability_contexts: tuple[ShadowEvidenceContext | None, ...] | None = None


@dataclass(frozen=True)
class ShadowScenarioReport:
    """Auditable report line for one scenario."""

    scenario_id: str

    normative_decision: str | None
    readiness_decision: str | None
    operational_gate_decision: str | None

    normative_error: str | None
    readiness_error: str | None
    operational_gate_error: str | None

    divergences: tuple[str, ...]

    classification: ShadowReportClassification

    # Comparable means: technical comparability of the three evaluator decisions
    # in this synthetic scenario, not identity of dataset/execution.
    comparable: bool

    # Traceability is evaluated separately from decision comparability.
    traceability_status: TraceabilityStatus
    policy_identity_status: PolicyIdentityStatus
    traceability_reasons: tuple[str, ...]

    # Auditably comparable means we can prove shared context and shared policy.
    auditably_comparable: bool

    @property
    def report_authorizes_publication(self) -> bool:
        return False


@dataclass(frozen=True)
class ShadowDivergenceReport:
    scenarios: tuple[ShadowScenarioReport, ...]

    @property
    def report_authorizes_publication(self) -> bool:
        return False


def _classify_comparison(
    comparison: NormativeShadowComparison,
) -> tuple[ShadowReportClassification, bool]:
    errors = [
        comparison.normative_error,
        comparison.readiness_error,
        comparison.operational_gate_error,
    ]
    has_invalid = any(err is not None and err.startswith("invalid:") for err in errors)
    has_unavailable = any(
        err is not None and err.startswith("unavailable:") for err in errors
    )

    comparable = (
        comparison.normative is not None
        and comparison.readiness is not None
        and comparison.operational_gate is not None
        and not has_invalid
        and not has_unavailable
    )

    if has_invalid:
        return "invalid", comparable
    if has_unavailable:
        return "unavailable", comparable

    if comparable:
        if comparison.divergences:
            return "divergence", comparable
        return "agreement", comparable

    if comparison.divergences:
        return "divergence", comparable
    return "inconclusive", comparable


def _assess_traceability_for_scenario(
    scenario: ShadowScenario,
) -> TraceabilityAssessment:
    if scenario.traceability_contexts is None:
        return TraceabilityAssessment(
            status="insufficient",
            policy_identity_status="insufficient",
            reasons=("No traceability contexts provided.",),
        )

    return assess_shadow_traceability(scenario.traceability_contexts)


def build_shadow_divergence_report(
    scenarios: Iterable[ShadowScenario],
) -> ShadowDivergenceReport:
    """Build a deterministic, purely synthetic shadow divergence report.

    - No IO
    - No network calls
    - No operational authorization
    - Stable ordering by `scenario_id`
    """

    scenario_list = list(scenarios)
    ids = [scenario.scenario_id for scenario in scenario_list]
    duplicates = sorted({scenario_id for scenario_id in ids if ids.count(scenario_id) > 1})
    if duplicates:
        raise ValueError(
            "Scenario ids must be unique. Duplicates: " + ", ".join(duplicates)
        )

    reports: list[ShadowScenarioReport] = []
    for scenario in scenario_list:
        comparison = compare_normative_shadow(
            policy=scenario.policy,
            normative_evidence=scenario.normative_evidence,
            readiness_evidence=scenario.readiness_evidence,
            operational_gate_evidence=scenario.operational_gate_evidence,
        )
        classification, comparable = _classify_comparison(comparison)

        traceability = _assess_traceability_for_scenario(scenario)
        auditably_comparable = (
            comparable
            and traceability.status == "compatible"
            and traceability.policy_identity_status == "proven"
        )

        reports.append(
            ShadowScenarioReport(
                scenario_id=scenario.scenario_id,
                normative_decision=(
                    comparison.normative.decision if comparison.normative is not None else None
                ),
                readiness_decision=(
                    comparison.readiness.decision if comparison.readiness is not None else None
                ),
                operational_gate_decision=(
                    comparison.operational_gate.decision
                    if comparison.operational_gate is not None
                    else None
                ),
                normative_error=comparison.normative_error,
                readiness_error=comparison.readiness_error,
                operational_gate_error=comparison.operational_gate_error,
                divergences=comparison.divergences,
                classification=classification,
                comparable=comparable,
                traceability_status=traceability.status,
                policy_identity_status=traceability.policy_identity_status,
                traceability_reasons=traceability.reasons,
                auditably_comparable=auditably_comparable,
            )
        )

    reports_sorted = tuple(sorted(reports, key=lambda item: item.scenario_id))
    return ShadowDivergenceReport(scenarios=reports_sorted)
