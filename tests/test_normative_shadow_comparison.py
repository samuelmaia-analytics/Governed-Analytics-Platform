from __future__ import annotations

import pytest

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


def _base_policy(*, minimum_quality_score: int = 80) -> NormativePublicationPolicy:
    return NormativePublicationPolicy(
        minimum_quality_score=minimum_quality_score,
        maximum_privacy_risk_score=60,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=(
            "critical_rule_failures_gt_0",
            "schema_contract_failed",
            "sensitive_data_without_protection",
            "privacy_risk_score_gt_maximum",
            "freshness_stale",
        ),
    )


def _evidence(*, data_quality_score: int) -> NormativeEvidence:
    return NormativeEvidence(
        data_quality_score=data_quality_score,
        privacy_risk_score=10,
        freshness_status="fresh",
        schema_contract_status="passed",
        critical_rule_failures=0,
        has_sensitive_data_without_protection=False,
    )


def _readiness_evidence(*, data_quality_score: int) -> PublicationReadinessEvidence:
    return PublicationReadinessEvidence(
        data_quality_score=data_quality_score,
        privacy_risk_score=10,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )


def _operational_gate_all_pass() -> OperationalGateEvidence:
    return OperationalGateEvidence(
        total_checks=10,
        pass_checks=10,
        warn_checks=0,
        fail_checks=0,
        critical_failures=0,
        privacy_failed_checks=0,
    )


def test_shadow_never_authorizes_even_when_all_allow() -> None:
    comparison = compare_normative_shadow(
        policy=_base_policy(),
        normative_evidence=_evidence(data_quality_score=95),
        readiness_evidence=_readiness_evidence(data_quality_score=95),
        operational_gate_evidence=_operational_gate_all_pass(),
    )

    assert comparison.normative is not None
    assert comparison.normative.authorized is True
    assert comparison.readiness is not None
    assert comparison.readiness.decision == "Approved"
    assert comparison.operational_gate is not None
    assert comparison.operational_gate.decision == "APPROVED"

    assert comparison.shadow_authorizes_publication is False



def test_shadow_result_cannot_be_forced_to_authorize() -> None:
    with pytest.raises(TypeError):
        NormativeShadowComparison(
            normative=None,
            readiness=None,
            operational_gate=None,
            shadow_authorizes_publication=True,
        )



def test_shadow_detects_divergence_readiness_approved_normative_blocked() -> None:
    comparison = compare_normative_shadow(
        policy=_base_policy(minimum_quality_score=95),
        normative_evidence=_evidence(data_quality_score=90),
        readiness_evidence=_readiness_evidence(data_quality_score=90),
        operational_gate_evidence=_operational_gate_all_pass(),
    )

    assert comparison.normative is not None
    assert comparison.normative.authorized is False
    assert comparison.readiness is not None
    assert comparison.readiness.decision == "Approved"
    assert comparison.operational_gate is not None
    assert comparison.operational_gate.decision == "APPROVED"

    assert any(
        "Readiness esta Approved, mas normativa nao autoriza" in msg
        for msg in comparison.divergences
    )
    assert any(
        "Gate operacional autorizou, mas normativa nao autoriza" in msg
        for msg in comparison.divergences
    )
    assert comparison.shadow_authorizes_publication is False


def test_shadow_detects_divergence_normative_authorizes_readiness_needs_review() -> None:
    comparison = compare_normative_shadow(
        policy=_base_policy(minimum_quality_score=70),
        normative_evidence=_evidence(data_quality_score=79),
        readiness_evidence=_readiness_evidence(data_quality_score=79),
        operational_gate_evidence=_operational_gate_all_pass(),
    )

    assert comparison.normative is not None
    assert comparison.normative.authorized is True
    assert comparison.readiness is not None
    assert comparison.readiness.decision == "Needs Review"

    assert any(
        "Normativa autoriza, mas readiness nao esta Approved" in msg
        for msg in comparison.divergences
    )
    assert comparison.shadow_authorizes_publication is False


def test_shadow_detects_divergence_readiness_vs_operational_gate() -> None:
    operational_gate_blocked = OperationalGateEvidence(
        total_checks=10,
        pass_checks=9,
        warn_checks=0,
        fail_checks=1,
        critical_failures=0,
        privacy_failed_checks=0,
    )
    comparison = compare_normative_shadow(
        policy=_base_policy(minimum_quality_score=70),
        normative_evidence=_evidence(data_quality_score=95),
        readiness_evidence=_readiness_evidence(data_quality_score=95),
        operational_gate_evidence=operational_gate_blocked,
    )

    assert comparison.readiness is not None
    assert comparison.readiness.decision == "Approved"
    assert comparison.operational_gate is not None
    assert comparison.operational_gate.decision == "BLOCKED"

    assert any(
        "Readiness esta Approved, mas gate operacional bloqueou" in msg
        for msg in comparison.divergences
    )
    assert comparison.shadow_authorizes_publication is False


def test_shadow_handles_missing_evidence_without_approving() -> None:
    comparison = compare_normative_shadow(
        policy=_base_policy(),
        normative_evidence=_evidence(data_quality_score=95),
        readiness_evidence=None,
        operational_gate_evidence=None,
    )

    assert comparison.readiness is None
    assert comparison.operational_gate is None
    assert comparison.normative is not None
    assert comparison.normative.authorized is True

    assert comparison.readiness_error is not None
    assert comparison.operational_gate_error is not None

    assert any(
        "Readiness unavailable/invalid" in msg
        for msg in comparison.divergences
    )
    assert any(
        "Operational gate unavailable/invalid" in msg
        for msg in comparison.divergences
    )

    assert comparison.shadow_authorizes_publication is False


def test_shadow_handles_invalid_policy_as_controlled_error() -> None:
    invalid_policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=60,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=(),
    )

    comparison = compare_normative_shadow(
        policy=invalid_policy,
        normative_evidence=_evidence(data_quality_score=95),
        readiness_evidence=_readiness_evidence(data_quality_score=95),
        operational_gate_evidence=_operational_gate_all_pass(),
    )

    assert comparison.normative is None
    assert comparison.normative_error is not None
    assert any(
        "Normative invalid" in msg
        for msg in comparison.divergences
    )
    assert comparison.shadow_authorizes_publication is False


def test_shadow_is_deterministic_for_same_inputs() -> None:
    policy = _base_policy(minimum_quality_score=95)
    evidence = _evidence(data_quality_score=90)
    readiness = _readiness_evidence(data_quality_score=90)
    gate = _operational_gate_all_pass()

    first = compare_normative_shadow(
        policy=policy,
        normative_evidence=evidence,
        readiness_evidence=readiness,
        operational_gate_evidence=gate,
    )
    second = compare_normative_shadow(
        policy=policy,
        normative_evidence=evidence,
        readiness_evidence=readiness,
        operational_gate_evidence=gate,
    )

    assert first == second