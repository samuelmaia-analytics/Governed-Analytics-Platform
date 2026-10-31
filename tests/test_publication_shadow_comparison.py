from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from src.publication_evidence.models import PublicationEvidence
from src.publication_gate import PublicationReadinessDecision
from src.publication_provenance.models import (
    EvidenceSource,
    ProvenanceValidationResult,
)
from src.publication_shadow.comparison import (
    ShadowDivergenceType,
    compare_publication_shadow,
)
from src.publication_shadow.evaluation import (
    ShadowPublicationEvaluation,
    evaluate_publication_shadow,
)


def valid_provenance() -> ProvenanceValidationResult:
    return ProvenanceValidationResult(
        valid=True,
        current_run_id="run-x",
        current_sources=(
            EvidenceSource.OPERATIONAL_QUALITY,
            EvidenceSource.SCHEMA_CONTRACTS,
            EvidenceSource.PRIVACY,
            EvidenceSource.MONITORING,
            EvidenceSource.CLASSIFICATION,
        ),
        missing_sources=(),
        foreign_run_sources=(),
        unknown_sources=(),
        reasons=(),
    )


def shadow(
    historical: str,
    canonical: str,
    *,
    severity: str = "Low",
) -> ShadowPublicationEvaluation:
    decision = PublicationReadinessDecision(
        decision=canonical,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        reasons=["canonical reason"],
        required_actions=["canonical action"],
    )
    return ShadowPublicationEvaluation(
        evaluated=True,
        canonical_decision=decision,
        current_monitor_decision=historical,  # type: ignore[arg-type]
        diverged=historical != canonical,
        unavailable_inputs=(),
    )


def healthy_evidence() -> PublicationEvidence:
    return PublicationEvidence(
        quality_status="PASS",
        quality_score=100,
        quality_failed_checks=0,
        quality_warning_checks=0,
        critical_quality_failures=0,
        schema_status="PASS",
        business_rules_status="PASS",
        business_rule_failed_checks=0,
        privacy_risk_score=20,
        privacy_controls_status="PASS",
        privacy_failed_checks=0,
        sensitive_data_protected=True,
        freshness_status="fresh",
        monitoring_status="PASS",
        monitoring_failed_checks=0,
        observability_status="PASS",
        observability_failed_checks=0,
        observability_insufficient_history_checks=0,
    )
@pytest.mark.parametrize(
    ("historical", "canonical"),
    [("Approved", "Approved"), ("Needs Review", "Needs Review")],
)
def test_equal_statuses_are_agreement(historical: str, canonical: str) -> None:
    comparison = compare_publication_shadow(
        shadow(historical, canonical), valid_provenance()
    )

    assert comparison.evaluated is True
    assert comparison.diverged is False
    assert comparison.divergence_type is ShadowDivergenceType.AGREEMENT


@pytest.mark.parametrize(
    ("historical", "canonical"),
    [
        ("Approved", "Needs Review"),
        ("Approved", "Blocked"),
        ("Needs Review", "Blocked"),
    ],
)
def test_more_restrictive_canonical_status_is_classified(
    historical: str, canonical: str
) -> None:
    comparison = compare_publication_shadow(
        shadow(historical, canonical, severity="Critical"), valid_provenance()
    )

    assert comparison.diverged is True
    assert comparison.divergence_type is ShadowDivergenceType.CANONICAL_STRICTER
    assert comparison.canonical_severity == "Critical"


def test_more_restrictive_historical_status_is_classified() -> None:
    comparison = compare_publication_shadow(
        shadow("Needs Review", "Approved"), valid_provenance()
    )

    assert comparison.diverged is True
    assert comparison.divergence_type is ShadowDivergenceType.HISTORICAL_STRICTER


def test_unavailable_shadow_has_no_invented_canonical_status() -> None:
    provenance = ProvenanceValidationResult(
        valid=False,
        current_run_id="run-x",
        current_sources=(EvidenceSource.MONITORING,),
        missing_sources=(EvidenceSource.OPERATIONAL_QUALITY,),
        foreign_run_sources=(EvidenceSource.SCHEMA_CONTRACTS,),
        unknown_sources=(EvidenceSource.PRIVACY,),
        reasons=("operational_quality: missing",),
    )
    unavailable = ShadowPublicationEvaluation(
        False,
        None,
        "Approved",
        None,
        (
            "operational_quality: missing",
            "schema_contracts: foreign run_id 'run-y' (current 'run-x')",
        ),
    )

    comparison = compare_publication_shadow(unavailable, provenance)

    assert comparison.evaluated is False
    assert comparison.canonical_decision is None
    assert comparison.canonical_severity is None
    assert comparison.diverged is None
    assert comparison.divergence_type is ShadowDivergenceType.UNAVAILABLE
    assert comparison.provenance_valid is False
    assert comparison.missing_sources == (EvidenceSource.OPERATIONAL_QUALITY,)
    assert comparison.foreign_run_sources == (EvidenceSource.SCHEMA_CONTRACTS,)
    assert comparison.unknown_sources == (EvidenceSource.PRIVACY,)


def test_reasons_actions_and_run_id_are_copied_into_frozen_diagnostics() -> None:
    source_shadow = shadow("Approved", "Needs Review", severity="Medium")
    comparison = compare_publication_shadow(source_shadow, valid_provenance())
    assert source_shadow.canonical_decision is not None
    source_shadow.canonical_decision.reasons.append("later mutation")

    assert comparison.run_id == "run-x"
    assert comparison.canonical_reasons == ("canonical reason",)
    assert comparison.canonical_required_actions == ("canonical action",)
    with pytest.raises(FrozenInstanceError):
        comparison.run_id = "run-y"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("historical", "evidence", "canonical", "divergence_type"),
    [
        (
            "Approved",
            replace(healthy_evidence(), quality_score=69),
            "Needs Review",
            ShadowDivergenceType.CANONICAL_STRICTER,
        ),
        (
            "Approved",
            replace(healthy_evidence(), schema_status="FAIL"),
            "Blocked",
            ShadowDivergenceType.CANONICAL_STRICTER,
        ),
        (
            "Needs Review",
            replace(healthy_evidence(), schema_status="FAIL"),
            "Blocked",
            ShadowDivergenceType.CANONICAL_STRICTER,
        ),
        (
            "Needs Review",
            healthy_evidence(),
            "Approved",
            ShadowDivergenceType.HISTORICAL_STRICTER,
        ),
    ],
)
def test_comparison_classifies_real_shadow_policy_results(
    historical: str,
    evidence: PublicationEvidence,
    canonical: str,
    divergence_type: ShadowDivergenceType,
) -> None:
    evaluated_shadow = evaluate_publication_shadow(
        evidence,
        current_monitor_decision=historical,  # type: ignore[arg-type]
    )

    comparison = compare_publication_shadow(evaluated_shadow, valid_provenance())

    assert comparison.canonical_decision == canonical
    assert comparison.divergence_type is divergence_type


@pytest.mark.parametrize(
    ("field", "expected_unavailable"),
    [
        ("quality_score", "quality_score"),
        ("privacy_risk_score", "privacy_risk_score"),
        ("sensitive_data_protected", "sensitive_data_protected"),
    ],
)
def test_complete_provenance_does_not_hide_incomplete_evidence(
    field: str, expected_unavailable: str
) -> None:
    evidence = replace(healthy_evidence(), **{field: None})
    unavailable_shadow = evaluate_publication_shadow(
        evidence, current_monitor_decision="Approved"
    )

    comparison = compare_publication_shadow(
        unavailable_shadow, valid_provenance()
    )

    assert comparison.provenance_valid is True
    assert comparison.evaluated is False
    assert comparison.divergence_type is ShadowDivergenceType.UNAVAILABLE
    assert comparison.canonical_decision is None
    assert comparison.unavailable_inputs == (expected_unavailable,)
