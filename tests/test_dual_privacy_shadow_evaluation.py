from __future__ import annotations

from dataclasses import replace

import pytest

from src.publication_evidence.models import PublicationEvidence
from src.publication_provenance import EvidenceProvenance, EvidenceSource
from src.publication_shadow import evaluate_dual_privacy_shadow


def _evidence(*, protected: bool) -> PublicationEvidence:
    return PublicationEvidence(
        quality_status="PASS",
        quality_score=100,
        quality_failed_checks=0,
        quality_warning_checks=0,
        critical_quality_failures=0,
        schema_status="PASS",
        business_rules_status="PASS",
        business_rule_failed_checks=0,
        privacy_risk_score=100,
        privacy_controls_status="PASS",
        privacy_failed_checks=0,
        sensitive_data_protected=protected,
        freshness_status="fresh",
        monitoring_status="PASS",
        monitoring_failed_checks=0,
        observability_status="PASS",
        observability_failed_checks=0,
        observability_insufficient_history_checks=0,
    )


def _provenance(run_id: str | None = "run-x") -> EvidenceProvenance:
    return EvidenceProvenance(EvidenceSource.PRIVACY, run_id)


@pytest.mark.parametrize(
    ("protected", "residual_score", "inherent_decision", "residual_decision"),
    [
        (True, 20, "Needs Review", "Approved"),
        (False, 20, "Blocked", "Blocked"),
        (True, 80, "Needs Review", "Needs Review"),
    ],
)
def test_dual_evaluation_varies_only_privacy_score(
    protected: bool,
    residual_score: int,
    inherent_decision: str,
    residual_decision: str,
) -> None:
    result = evaluate_dual_privacy_shadow(
        _evidence(protected=protected),
        inherent_privacy_risk_score=100,
        residual_privacy_risk_score=residual_score,
        inherent_provenance=_provenance(),
        residual_provenance=_provenance(),
        current_run_id="run-x",
        current_monitor_decision="Approved",
    )

    assert result.inherent.evaluated is True
    assert result.residual.evaluated is True
    assert result.inherent.canonical_decision is not None
    assert result.residual.canonical_decision is not None
    assert result.inherent.canonical_decision.decision == inherent_decision
    assert result.residual.canonical_decision.decision == residual_decision
    assert result.inherent_privacy_risk_score == 100
    assert result.residual_privacy_risk_score == residual_score


def test_foreign_run_residual_is_unavailable_without_affecting_inherent() -> None:
    result = evaluate_dual_privacy_shadow(
        _evidence(protected=True),
        inherent_privacy_risk_score=100,
        residual_privacy_risk_score=20,
        inherent_provenance=_provenance(),
        residual_provenance=replace(_provenance(), run_id="run-y"),
        current_run_id="run-x",
        current_monitor_decision="Approved",
    )

    assert result.inherent.evaluated is True
    assert result.residual.evaluated is False
    assert result.residual.canonical_decision is None
    assert "foreign run_id 'run-y'" in result.residual.unavailable_inputs[0]
