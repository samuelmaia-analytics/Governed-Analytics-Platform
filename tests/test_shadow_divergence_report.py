from __future__ import annotations

import pytest

from src.normative_publication_policy import (
    NormativeEvidence,
    NormativePublicationPolicy,
)
from src.publication_shadow.divergence_report import (
    ShadowScenario,
    build_shadow_divergence_report,
)
from src.publication_shadow.normative_comparison import (
    OperationalGateEvidence,
    PublicationReadinessEvidence,
)
from src.publication_shadow.traceability import (
    ShadowEvidenceContext,
    fingerprint_normative_policy,
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


def _assert_default_traceability_is_insufficient(scenario) -> None:
    assert scenario.traceability_status == "insufficient"
    assert scenario.policy_identity_status == "insufficient"
    assert scenario.auditably_comparable is False
    assert scenario.traceability_reasons == ("No traceability contexts provided.",)


def test_report_agreement_is_comparable_and_never_authorizes() -> None:
    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="agreement",
                policy=_base_policy(),
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
            )
        ]
    )

    assert report.report_authorizes_publication is False
    assert len(report.scenarios) == 1
    scenario = report.scenarios[0]

    assert scenario.scenario_id == "agreement"
    assert scenario.classification == "agreement"
    assert scenario.comparable is True
    assert scenario.divergences == ()
    assert scenario.report_authorizes_publication is False
    _assert_default_traceability_is_insufficient(scenario)


def test_report_divergence_is_comparable() -> None:
    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="divergence",
                policy=_base_policy(minimum_quality_score=95),
                normative_evidence=_evidence(data_quality_score=90),
                readiness_evidence=_readiness_evidence(data_quality_score=90),
                operational_gate_evidence=_operational_gate_all_pass(),
            )
        ]
    )

    scenario = report.scenarios[0]
    assert scenario.classification == "divergence"
    assert scenario.comparable is True
    assert scenario.divergences
    assert scenario.report_authorizes_publication is False
    _assert_default_traceability_is_insufficient(scenario)


def test_report_unavailable_when_evidence_missing() -> None:
    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="unavailable",
                policy=_base_policy(),
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=None,
                operational_gate_evidence=None,
            )
        ]
    )

    scenario = report.scenarios[0]
    assert scenario.classification == "unavailable"
    assert scenario.comparable is False
    assert scenario.report_authorizes_publication is False
    _assert_default_traceability_is_insufficient(scenario)


def test_report_invalid_when_policy_invalid() -> None:
    invalid_policy = NormativePublicationPolicy(
        minimum_quality_score=80,
        maximum_privacy_risk_score=60,
        freshness_requirement="fresh",
        contract_required=True,
        blocking_conditions=(),
    )

    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="invalid",
                policy=invalid_policy,
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
            )
        ]
    )

    scenario = report.scenarios[0]
    assert scenario.classification == "invalid"
    assert scenario.comparable is False
    assert scenario.normative_decision is None
    _assert_default_traceability_is_insufficient(scenario)


def test_report_auditably_comparable_is_false_when_policy_identity_is_not_proven() -> None:
    policy = _base_policy()
    fp = fingerprint_normative_policy(policy)

    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="audit-not-proven",
                policy=policy,
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
                traceability_contexts=(
                    ShadowEvidenceContext(
                        evaluator_name="normative",
                        dataset_id="fact_orders_dashboard",
                        execution_id="run-123",
                        policy_fingerprint=fp,
                        evidence_origin="synthetic",
                    ),
                    ShadowEvidenceContext(
                        evaluator_name="readiness",
                        dataset_id="fact_orders_dashboard",
                        execution_id="run-123",
                        policy_fingerprint=fp,
                        evidence_origin="synthetic",
                    ),
                    ShadowEvidenceContext(
                        evaluator_name="operational_gate",
                        dataset_id="fact_orders_dashboard",
                        execution_id="run-123",
                        policy_fingerprint=None,
                        evidence_origin="synthetic",
                    ),
                ),
            )
        ]
    )

    scenario = report.scenarios[0]
    assert scenario.comparable is True
    assert scenario.traceability_status == "compatible"
    assert scenario.policy_identity_status == "not_proven"
    assert scenario.auditably_comparable is False


def test_report_auditably_comparable_is_true_when_policy_identity_is_proven_and_decisions_are_comparable() -> None:
    policy = _base_policy()
    fp = fingerprint_normative_policy(policy)

    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="audit-proven",
                policy=policy,
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
                traceability_contexts=(
                    ShadowEvidenceContext(
                        evaluator_name="normative",
                        dataset_id="fact_orders_dashboard",
                        execution_id="run-123",
                        policy_fingerprint=fp,
                        evidence_origin="synthetic",
                    ),
                    ShadowEvidenceContext(
                        evaluator_name="readiness",
                        dataset_id="fact_orders_dashboard",
                        execution_id="run-123",
                        policy_fingerprint=fp,
                        evidence_origin="synthetic",
                    ),
                    ShadowEvidenceContext(
                        evaluator_name="operational_gate",
                        dataset_id="fact_orders_dashboard",
                        execution_id="run-123",
                        policy_fingerprint=fp,
                        evidence_origin="synthetic",
                    ),
                ),
            )
        ]
    )

    scenario = report.scenarios[0]
    assert scenario.comparable is True
    assert scenario.traceability_status == "compatible"
    assert scenario.policy_identity_status == "proven"
    assert scenario.auditably_comparable is True
    assert scenario.report_authorizes_publication is False


def test_report_auditably_comparable_is_false_when_dataset_is_incompatible() -> None:
    policy = _base_policy()
    fp = fingerprint_normative_policy(policy)

    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="audit-incompatible",
                policy=policy,
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
                traceability_contexts=(
                    ShadowEvidenceContext(
                        evaluator_name="normative",
                        dataset_id="dataset_a",
                        execution_id="run-123",
                        policy_fingerprint=fp,
                        evidence_origin="synthetic",
                    ),
                    ShadowEvidenceContext(
                        evaluator_name="readiness",
                        dataset_id="dataset_b",
                        execution_id="run-123",
                        policy_fingerprint=fp,
                        evidence_origin="synthetic",
                    ),
                    ShadowEvidenceContext(
                        evaluator_name="operational_gate",
                        dataset_id="dataset_a",
                        execution_id="run-123",
                        policy_fingerprint=fp,
                        evidence_origin="synthetic",
                    ),
                ),
            )
        ]
    )

    scenario = report.scenarios[0]
    assert scenario.comparable is True
    assert scenario.traceability_status == "incompatible"
    assert scenario.auditably_comparable is False


def test_report_is_sorted_deterministically_by_id() -> None:
    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="b",
                policy=_base_policy(),
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
            ),
            ShadowScenario(
                scenario_id="a",
                policy=_base_policy(),
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
            ),
        ]
    )

    assert [scenario.scenario_id for scenario in report.scenarios] == ["a", "b"]


def test_report_rejects_duplicate_scenario_ids() -> None:
    with pytest.raises(ValueError, match="Duplicates"):
        build_shadow_divergence_report(
            [
                ShadowScenario(
                    scenario_id="dup",
                    policy=_base_policy(),
                    normative_evidence=_evidence(data_quality_score=95),
                    readiness_evidence=_readiness_evidence(data_quality_score=95),
                    operational_gate_evidence=_operational_gate_all_pass(),
                ),
                ShadowScenario(
                    scenario_id="dup",
                    policy=_base_policy(),
                    normative_evidence=_evidence(data_quality_score=95),
                    readiness_evidence=_readiness_evidence(data_quality_score=95),
                    operational_gate_evidence=_operational_gate_all_pass(),
                ),
            ]
        )


def test_report_allows_empty_input() -> None:
    report = build_shadow_divergence_report([])

    assert report.scenarios == ()
    assert report.report_authorizes_publication is False
