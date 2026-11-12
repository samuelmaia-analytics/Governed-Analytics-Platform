from __future__ import annotations

import pytest

from src.normative_publication_policy import NormativePublicationPolicy
from src.publication_shadow.traceability import (
    ShadowEvidenceContext,
    assess_shadow_traceability,
    fingerprint_normative_policy,
)


def _policy(*, minimum_quality_score: int = 80) -> NormativePublicationPolicy:
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


def _ctx(
    evaluator_name: str,
    *,
    dataset_id: str | None = "fact_orders_dashboard",
    execution_id: str | None = "run-123",
    policy_fingerprint: str | None = None,
) -> ShadowEvidenceContext:
    return ShadowEvidenceContext(
        evaluator_name=evaluator_name,  # type: ignore[arg-type]
        dataset_id=dataset_id,
        execution_id=execution_id,
        policy_fingerprint=policy_fingerprint,
        evidence_origin="synthetic",
    )


def test_traceability_compatible_with_three_evaluators_same_dataset_and_execution() -> None:
    assessment = assess_shadow_traceability(
        [
            _ctx("normative"),
            _ctx("readiness"),
            _ctx("operational_gate"),
        ]
    )

    assert assessment.status == "compatible"
    assert assessment.context_compatible is True
    assert assessment.policy_identity_status == "not_proven"
    assert assessment.policy_identity_proven is False
    assert assessment.authorizes_publication is False
    assert assessment.reasons == ("policy_fingerprint not available for comparison.",)


def test_traceability_requires_all_three_evaluators() -> None:
    assessment = assess_shadow_traceability(
        [
            _ctx("normative"),
            _ctx("readiness"),
        ]
    )

    assert assessment.status == "insufficient"
    assert assessment.policy_identity_status == "insufficient"


def test_traceability_rejects_duplicate_evaluator_names() -> None:
    assessment = assess_shadow_traceability(
        [
            _ctx("normative"),
            _ctx("normative"),
            _ctx("readiness"),
        ]
    )

    assert assessment.status == "insufficient"
    assert assessment.policy_identity_status == "insufficient"


def test_invalid_evaluator_name_is_rejected_at_runtime() -> None:
    with pytest.raises(ValueError, match="Unknown evaluator_name"):
        _ctx("unknown")


def test_traceability_insufficient_for_whitespace_only_identifiers() -> None:
    assessment = assess_shadow_traceability(
        [
            _ctx("normative", dataset_id="   "),
            _ctx("readiness"),
            _ctx("operational_gate"),
        ]
    )

    assert assessment.status == "insufficient"
    assert assessment.policy_identity_status == "insufficient"


def test_traceability_incompatible_when_dataset_differs() -> None:
    assessment = assess_shadow_traceability(
        [
            _ctx("normative", dataset_id="dataset_a"),
            _ctx("readiness", dataset_id="dataset_b"),
            _ctx("operational_gate", dataset_id="dataset_a"),
        ]
    )

    assert assessment.status == "incompatible"
    assert assessment.policy_identity_status == "insufficient"


def test_traceability_incompatible_when_execution_differs() -> None:
    assessment = assess_shadow_traceability(
        [
            _ctx("normative", execution_id="run-1"),
            _ctx("readiness", execution_id="run-2"),
            _ctx("operational_gate", execution_id="run-1"),
        ]
    )

    assert assessment.status == "incompatible"
    assert assessment.policy_identity_status == "insufficient"


def test_traceability_policy_identity_proven_requires_three_valid_equal_fingerprints() -> None:
    fp = fingerprint_normative_policy(_policy())

    assessment = assess_shadow_traceability(
        [
            _ctx("normative", policy_fingerprint=fp),
            _ctx("readiness", policy_fingerprint=fp),
            _ctx("operational_gate", policy_fingerprint=fp),
        ]
    )

    assert assessment.status == "compatible"
    assert assessment.policy_identity_status == "proven"
    assert assessment.policy_identity_proven is True


def test_traceability_two_fingerprints_equal_one_missing_is_not_proven() -> None:
    fp = fingerprint_normative_policy(_policy())

    assessment = assess_shadow_traceability(
        [
            _ctx("normative", policy_fingerprint=fp),
            _ctx("readiness", policy_fingerprint=fp),
            _ctx("operational_gate"),
        ]
    )

    assert assessment.status == "compatible"
    assert assessment.policy_identity_status == "not_proven"
    assert assessment.policy_identity_proven is False


def test_traceability_invalid_fingerprint_is_insufficient_even_if_only_one_provided() -> None:
    assessment = assess_shadow_traceability(
        [
            _ctx("normative", policy_fingerprint="sha256:aaa"),
            _ctx("readiness"),
            _ctx("operational_gate"),
        ]
    )

    assert assessment.status == "compatible"
    assert assessment.policy_identity_status == "insufficient"


def test_traceability_policy_fingerprint_conflict_is_incompatible() -> None:
    fp_a = "sha256:" + ("a" * 64)
    fp_b = "sha256:" + ("b" * 64)

    assessment = assess_shadow_traceability(
        [
            _ctx("normative", policy_fingerprint=fp_a),
            _ctx("readiness", policy_fingerprint=fp_b),
            _ctx("operational_gate", policy_fingerprint=fp_a),
        ]
    )

    assert assessment.status == "compatible"
    assert assessment.policy_identity_status == "incompatible"


def test_traceability_rejects_unsupported_policy_fingerprint_semantic() -> None:
    assessment = assess_shadow_traceability(
        [
            _ctx("normative", policy_fingerprint="v1"),
            _ctx("readiness", policy_fingerprint="v1"),
            _ctx("operational_gate"),
        ]
    )

    assert assessment.status == "compatible"
    assert assessment.policy_identity_status == "insufficient"


def test_traceability_is_deterministic() -> None:
    contexts = [_ctx("normative"), _ctx("readiness"), _ctx("operational_gate")]

    assert assess_shadow_traceability(contexts) == assess_shadow_traceability(contexts)


def test_fingerprint_is_deterministic_and_changes_with_policy() -> None:
    base = fingerprint_normative_policy(_policy(minimum_quality_score=80))
    changed = fingerprint_normative_policy(_policy(minimum_quality_score=81))

    assert base == fingerprint_normative_policy(_policy(minimum_quality_score=80))
    assert base != changed
