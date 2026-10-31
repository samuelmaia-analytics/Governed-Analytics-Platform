from __future__ import annotations

from dataclasses import FrozenInstanceError, asdict, fields, replace

import pandas as pd
import pytest

from src.monitoring_components.models import MonitoringCheckResult
from src.publication_evidence.models import PublicationEvidence
from src.publication_gate import evaluate_publication_readiness
from src.publication_provenance.context import PipelineGovernanceContext
from src.publication_provenance.models import EvidenceProvenance, EvidenceSource
from src.publication_provenance.validation import (
    SHADOW_REQUIRED_SOURCES,
    validate_evidence_provenance,
)
from src.publication_shadow.evaluation import (
    ShadowPublicationEvaluation,
    evaluate_provenanced_publication_shadow,
    evaluate_publication_shadow,
)
from src.publish_components.models import PrivacyCheck
from src.quality_components.models import QualityCheckResult
from src.schema_contract_components.models import ContractCheck


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
        privacy_risk_score=0,
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


def test_shadow_model_fields_serialization_and_frozen_behavior() -> None:
    result = evaluate_publication_shadow(
        healthy_evidence(), current_monitor_decision="Approved"
    )

    assert [field.name for field in fields(result)] == [
        "evaluated",
        "canonical_decision",
        "current_monitor_decision",
        "diverged",
        "unavailable_inputs",
    ]
    assert asdict(result)["evaluated"] is True
    with pytest.raises(FrozenInstanceError):
        result.evaluated = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"quality_score": 79, "quality_status": "FAIL"},
        {"privacy_risk_score": 60},
        {"privacy_risk_score": 80},
        {"critical_quality_failures": 1, "quality_status": "FAIL"},
        {"schema_status": "FAIL"},
        {"sensitive_data_protected": False},
        {"freshness_status": "warning", "monitoring_status": "FAIL"},
        {"freshness_status": "stale", "monitoring_status": "FAIL"},
    ],
)
def test_complete_evidence_maps_exactly_to_domain_policy(
    changes: dict[str, object],
) -> None:
    evidence = replace(healthy_evidence(), **changes)  # type: ignore[arg-type]
    shadow = evaluate_publication_shadow(
        evidence, current_monitor_decision="Approved"
    )
    expected = evaluate_publication_readiness(
        data_quality_score=evidence.quality_score,  # type: ignore[arg-type]
        privacy_risk_score=evidence.privacy_risk_score,  # type: ignore[arg-type]
        critical_rule_failures=evidence.critical_quality_failures,  # type: ignore[arg-type]
        freshness_status=evidence.freshness_status,  # type: ignore[arg-type]
        schema_contract_status=(
            "passed" if evidence.schema_status == "PASS" else "failed"
        ),
        has_sensitive_data_without_protection=not evidence.sensitive_data_protected,
    )

    assert shadow.evaluated is True
    assert shadow.canonical_decision == expected
    assert shadow.unavailable_inputs == ()


@pytest.mark.parametrize(
    ("changes", "unavailable"),
    [
        ({"quality_score": None}, "quality_score"),
        ({"privacy_risk_score": None}, "privacy_risk_score"),
        ({"critical_quality_failures": None}, "critical_quality_failures"),
        ({"schema_status": "missing"}, "schema_status"),
        ({"schema_status": "unknown"}, "schema_status"),
        ({"sensitive_data_protected": None}, "sensitive_data_protected"),
        ({"freshness_status": "unknown"}, "freshness_status"),
    ],
)
def test_missing_or_unknown_input_prevents_silent_evaluation(
    changes: dict[str, object], unavailable: str
) -> None:
    result = evaluate_publication_shadow(
        replace(healthy_evidence(), **changes),  # type: ignore[arg-type]
        current_monitor_decision="Approved",
    )

    assert result == ShadowPublicationEvaluation(
        evaluated=False,
        canonical_decision=None,
        current_monitor_decision="Approved",
        diverged=None,
        unavailable_inputs=(unavailable,),
    )


@pytest.mark.parametrize(
    ("changes", "monitor", "canonical", "diverged"),
    [
        ({"quality_score": 69}, "Approved", "Needs Review", True),
        ({"privacy_risk_score": 60}, "Approved", "Needs Review", True),
        ({"schema_status": "FAIL"}, "Approved", "Blocked", True),
        ({}, "Needs Review", "Approved", True),
        ({}, "Approved", "Approved", False),
    ],
)
def test_shadow_divergence_is_diagnostic_only(
    changes: dict[str, object], monitor: str, canonical: str, diverged: bool
) -> None:
    result = evaluate_publication_shadow(
        replace(healthy_evidence(), **changes),  # type: ignore[arg-type]
        current_monitor_decision=monitor,  # type: ignore[arg-type]
    )

    assert result.current_monitor_decision == monitor
    assert result.canonical_decision is not None
    assert result.canonical_decision.decision == canonical
    assert result.diverged is diverged


def test_multiple_unavailable_inputs_preserve_deterministic_order() -> None:
    result = evaluate_publication_shadow(
        replace(
            healthy_evidence(),
            quality_score=None,
            privacy_risk_score=None,
            critical_quality_failures=None,
            schema_status="missing",
            sensitive_data_protected=None,
            freshness_status="unknown",
        ),
        current_monitor_decision="Needs Review",
    )

    assert result.evaluated is False
    assert result.unavailable_inputs == (
        "quality_score",
        "privacy_risk_score",
        "critical_quality_failures",
        "schema_status",
        "sensitive_data_protected",
        "freshness_status",
    )


def _checks(*, material_status: str = "PASS") -> list[PrivacyCheck]:
    return [
        PrivacyCheck("forbidden_columns_absent", material_status, "material"),
        PrivacyCheck("classification_leakage", material_status, "material"),
        PrivacyCheck("pseudonymized__customer_unique_id", "PASS", "token"),
    ]



def test_foreign_classification_keeps_shadow_unavailable() -> None:
    context = PipelineGovernanceContext("run-x")
    source = pd.DataFrame({"customer_unique_id": ["customer-1"]})
    published = pd.DataFrame({"customer_unique_id": ["cust_token"]})
    context.record_current_privacy(source, published, _checks())
    provenance = context.provenance[EvidenceSource.CLASSIFICATION]
    context.provenance[EvidenceSource.CLASSIFICATION] = EvidenceProvenance(
        source=EvidenceSource.CLASSIFICATION,
        run_id="run-y",
        produced_at=provenance.produced_at,
        execution_step=provenance.execution_step,
        dataset_name=provenance.dataset_name,
    )

    envelope = context.build_provenanced_evidence()
    validation = validate_evidence_provenance(
        envelope,
        {EvidenceSource.PRIVACY, EvidenceSource.CLASSIFICATION},
    )
    shadow = evaluate_provenanced_publication_shadow(
        envelope,
        required_sources=frozenset(
            {EvidenceSource.PRIVACY, EvidenceSource.CLASSIFICATION}
        ),
        current_monitor_decision="Approved",
    )

    assert validation.valid is False
    assert EvidenceSource.CLASSIFICATION in validation.foreign_run_sources
    assert shadow.evaluated is False


def test_complete_current_run_enables_shadow_without_changing_historical_decision() -> None:
    context = PipelineGovernanceContext("run-x")
    context.record_quality(
        [QualityCheckResult("quality", "PASS", 0.0, 0.0, "high", "ok")]
    )
    context.record_schema(
        [ContractCheck("dashboard", "published", "schema", "PASS", "ok")]
    )
    source = pd.DataFrame({"customer_unique_id": ["customer-1"]})
    published = pd.DataFrame({"customer_unique_id": ["cust_token"]})
    context.record_current_privacy(source, published, _checks())
    context.record_monitoring(
        [
            MonitoringCheckResult(
                "published_file_freshness_hours",
                "PASS",
                1.0,
                36.0,
                "high",
                "fresh",
            )
        ]
    )

    envelope = context.build_provenanced_evidence()
    validation = validate_evidence_provenance(
        envelope, SHADOW_REQUIRED_SOURCES
    )
    shadow = evaluate_provenanced_publication_shadow(
        envelope,
        required_sources=SHADOW_REQUIRED_SOURCES,
        current_monitor_decision="Approved",
    )

    assert validation.valid is True
    assert shadow.evaluated is True
    assert shadow.current_monitor_decision == "Approved"
    assert shadow.canonical_decision is not None
