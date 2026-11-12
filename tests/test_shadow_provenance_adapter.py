from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.normative_publication_policy import (
    NormativeEvidence,
    NormativePublicationPolicy,
)
from src.publication_provenance.models import EvidenceProvenance, EvidenceSource
from src.publication_shadow.divergence_report import (
    ShadowScenario,
    build_shadow_divergence_report,
)
from src.publication_shadow.normative_comparison import (
    OperationalGateEvidence,
    PublicationReadinessEvidence,
)
from src.publication_shadow.provenance_adapter import (
    EvaluatorProvenanceMetadata,
    adapt_explicit_provenance_to_shadow_contexts,
)
from src.publication_shadow.traceability import assess_shadow_traceability


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


def _prov(*, dataset_name: str | None, run_id: str | None) -> EvidenceProvenance:
    return EvidenceProvenance(
        source=EvidenceSource.SCHEMA_CONTRACTS,
        dataset_name=dataset_name,
        run_id=run_id,
    )


def test_adapter_three_explicit_origins_is_deterministic_and_non_operational() -> None:
    fp = "sha256:" + ("a" * 64)

    contexts_a = adapt_explicit_provenance_to_shadow_contexts(
        [
            EvaluatorProvenanceMetadata(
                evaluator_name="normative",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
                policy_fingerprint=fp,
                evidence_origin="normative-snapshot",
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="readiness",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
                evidence_origin="readiness-snapshot",
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="operational_gate",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
                evidence_origin="gate-snapshot",
            ),
        ]
    )

    contexts_b = adapt_explicit_provenance_to_shadow_contexts(
        [
            EvaluatorProvenanceMetadata(
                evaluator_name="operational_gate",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
                evidence_origin="gate-snapshot",
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="readiness",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
                evidence_origin="readiness-snapshot",
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="normative",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
                policy_fingerprint=fp,
                evidence_origin="normative-snapshot",
            ),
        ]
    )

    assert contexts_a == contexts_b
    assert contexts_a.authorizes_publication is False

    assessment = assess_shadow_traceability(contexts_a.as_tuple())
    assert assessment.status == "compatible"
    assert assessment.policy_identity_status == "not_proven"
    assert assessment.authorizes_publication is False

    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="agreement-traceability-not-proven",
                policy=_base_policy(),
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
                traceability_contexts=contexts_a.as_tuple(),
            )
        ]
    )

    scenario = report.scenarios[0]
    assert scenario.comparable is True
    assert scenario.traceability_status == "compatible"
    assert scenario.policy_identity_status == "not_proven"
    assert scenario.auditably_comparable is False
    assert report.report_authorizes_publication is False
    assert scenario.report_authorizes_publication is False


def test_adapter_only_one_origin_is_insufficient_and_never_auditably_comparable() -> None:
    contexts = adapt_explicit_provenance_to_shadow_contexts(
        [
            EvaluatorProvenanceMetadata(
                evaluator_name="normative",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
                evidence_origin="normative-only",
            )
        ]
    )

    assessment = assess_shadow_traceability(contexts.as_tuple())
    assert assessment.status == "insufficient"
    assert assessment.policy_identity_status == "insufficient"

    report = build_shadow_divergence_report(
        [
            ShadowScenario(
                scenario_id="agreement-insufficient-traceability",
                policy=_base_policy(),
                normative_evidence=_evidence(data_quality_score=95),
                readiness_evidence=_readiness_evidence(data_quality_score=95),
                operational_gate_evidence=_operational_gate_all_pass(),
                traceability_contexts=contexts.as_tuple(),
            )
        ]
    )

    scenario = report.scenarios[0]
    assert scenario.comparable is True
    assert scenario.auditably_comparable is False
    assert scenario.report_authorizes_publication is False


def test_adapter_dataset_absent_is_preserved_and_traceability_insufficient() -> None:
    contexts = adapt_explicit_provenance_to_shadow_contexts(
        [
            EvaluatorProvenanceMetadata(
                evaluator_name="normative",
                provenance=_prov(dataset_name=None, run_id="run-1"),
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="readiness",
                provenance=_prov(dataset_name=None, run_id="run-1"),
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="operational_gate",
                provenance=_prov(dataset_name=None, run_id="run-1"),
            ),
        ]
    )

    assert contexts.normative is not None
    assert contexts.normative.dataset_id is None

    assessment = assess_shadow_traceability(contexts.as_tuple())
    assert assessment.status == "insufficient"
    assert assessment.policy_identity_status == "insufficient"


def test_adapter_run_id_absent_is_preserved_and_traceability_insufficient() -> None:
    contexts = adapt_explicit_provenance_to_shadow_contexts(
        [
            EvaluatorProvenanceMetadata(
                evaluator_name="normative",
                provenance=_prov(dataset_name="dataset_a", run_id=None),
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="readiness",
                provenance=_prov(dataset_name="dataset_a", run_id=None),
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="operational_gate",
                provenance=_prov(dataset_name="dataset_a", run_id=None),
            ),
        ]
    )

    assessment = assess_shadow_traceability(contexts.as_tuple())
    assert assessment.status == "insufficient"
    assert assessment.policy_identity_status == "insufficient"


def test_adapter_datasets_divergent_is_incompatible() -> None:
    contexts = adapt_explicit_provenance_to_shadow_contexts(
        [
            EvaluatorProvenanceMetadata(
                evaluator_name="normative",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="readiness",
                provenance=_prov(dataset_name="dataset_b", run_id="run-1"),
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="operational_gate",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
            ),
        ]
    )

    assessment = assess_shadow_traceability(contexts.as_tuple())
    assert assessment.status == "incompatible"
    assert assessment.policy_identity_status == "insufficient"


def test_adapter_executions_divergent_is_incompatible() -> None:
    contexts = adapt_explicit_provenance_to_shadow_contexts(
        [
            EvaluatorProvenanceMetadata(
                evaluator_name="normative",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="readiness",
                provenance=_prov(dataset_name="dataset_a", run_id="run-2"),
            ),
            EvaluatorProvenanceMetadata(
                evaluator_name="operational_gate",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
            ),
        ]
    )

    assessment = assess_shadow_traceability(contexts.as_tuple())
    assert assessment.status == "incompatible"
    assert assessment.policy_identity_status == "insufficient"


def test_adapter_rejects_duplicate_evaluator_name() -> None:
    with pytest.raises(ValueError, match="Duplicate evaluator_name"):
        adapt_explicit_provenance_to_shadow_contexts(
            [
                EvaluatorProvenanceMetadata(evaluator_name="normative"),
                EvaluatorProvenanceMetadata(evaluator_name="normative"),
            ]
        )
def test_adapter_rejects_unknown_evaluator_name() -> None:
    # Literal typing does not validate at runtime; adapter must reject unknowns.
    with pytest.raises(ValueError, match="Unknown evaluator_name"):
        adapt_explicit_provenance_to_shadow_contexts(
            [EvaluatorProvenanceMetadata(evaluator_name="unknown")]  # type: ignore[arg-type]
        )


def test_adapter_rejects_whitespace_only_identifiers_as_contradictory() -> None:
    with pytest.raises(ValueError, match="dataset_name must not be empty"):
        adapt_explicit_provenance_to_shadow_contexts(
            [
                EvaluatorProvenanceMetadata(
                    evaluator_name="normative",
                    provenance=_prov(dataset_name="   ", run_id="run-1"),
                )
            ]
        )

    with pytest.raises(ValueError, match="run_id must not be empty"):
        adapt_explicit_provenance_to_shadow_contexts(
            [
                EvaluatorProvenanceMetadata(
                    evaluator_name="normative",
                    provenance=_prov(dataset_name="dataset_a", run_id="   "),
                )
            ]
        )


def test_adapter_immutability() -> None:
    contexts = adapt_explicit_provenance_to_shadow_contexts(
        [
            EvaluatorProvenanceMetadata(
                evaluator_name="normative",
                provenance=_prov(dataset_name="dataset_a", run_id="run-1"),
            )
        ]
    )

    with pytest.raises(FrozenInstanceError):
        contexts.normative = None  # type: ignore[misc]

    assert contexts.authorizes_publication is False
