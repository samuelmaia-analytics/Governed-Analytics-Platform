from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from typing import Any

import pytest

from src import publication_gate
from src.publication_evidence.models import PublicationEvidence
from src.publication_provenance import EvidenceProvenance, EvidenceSource
from src.publication_shadow import (
    DualPrivacyDivergenceType,
    compare_dual_privacy_policy,
)


def _evidence(*, protected: bool = True) -> PublicationEvidence:
    return PublicationEvidence(
        quality_status="PASS",
        quality_score=100,
        quality_failed_checks=0,
        quality_warning_checks=0,
        critical_quality_failures=0,
        schema_status="PASS",
        business_rules_status="PASS",
        business_rule_failed_checks=0,
        privacy_risk_score=999,
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


def _compare(
    inherent_score: int | None,
    residual_score: int | None,
    *,
    protected: bool = True,
    inherent_provenance: EvidenceProvenance | None = None,
    residual_provenance: EvidenceProvenance | None = None,
):
    return compare_dual_privacy_policy(
        _evidence(protected=protected),
        inherent_privacy_risk_score=inherent_score,
        residual_privacy_risk_score=residual_score,
        inherent_provenance=inherent_provenance or _provenance(),
        residual_provenance=residual_provenance or _provenance(),
        current_run_id="run-x",
    )


@pytest.mark.parametrize(
    ("inherent_score", "residual_score", "decision"),
    [(50, 40, "Approved"), (86, 70, "Needs Review")],
)
def test_equal_policy_outcomes_are_agreement(
    inherent_score: int, residual_score: int, decision: str
) -> None:
    comparison = _compare(inherent_score, residual_score)

    assert comparison.evaluated is True
    assert comparison.inherent_decision == decision
    assert comparison.residual_decision == decision
    assert comparison.diverged is False
    assert comparison.divergence_type is DualPrivacyDivergenceType.AGREEMENT


def test_real_characterized_scores_make_residual_less_restrictive() -> None:
    comparison = _compare(86, 53, protected=True)

    assert comparison.run_id == "run-x"
    assert comparison.inherent_score == 86
    assert comparison.residual_score == 53
    assert comparison.inherent_decision == "Needs Review"
    assert comparison.inherent_severity == "High"
    assert comparison.residual_decision == "Approved"
    assert comparison.residual_severity == "Low"
    assert comparison.diverged is True
    assert (
        comparison.divergence_type
        is DualPrivacyDivergenceType.RESIDUAL_LESS_RESTRICTIVE
    )


def test_more_restrictive_residual_is_classified() -> None:
    comparison = _compare(53, 86)

    assert comparison.inherent_decision == "Approved"
    assert comparison.residual_decision == "Needs Review"
    assert comparison.diverged is True
    assert (
        comparison.divergence_type
        is DualPrivacyDivergenceType.RESIDUAL_MORE_RESTRICTIVE
    )


def test_unprotected_sensitive_data_blocks_both_branches() -> None:
    comparison = _compare(86, 53, protected=False)

    assert comparison.inherent_decision == "Blocked"
    assert comparison.residual_decision == "Blocked"
    assert comparison.inherent_severity == "Critical"
    assert comparison.residual_severity == "Critical"
    assert comparison.diverged is False
    assert comparison.divergence_type is DualPrivacyDivergenceType.AGREEMENT


def test_foreign_run_residual_makes_comparison_unavailable() -> None:
    comparison = _compare(
        86,
        53,
        residual_provenance=replace(_provenance(), run_id="run-y"),
    )

    assert comparison.evaluated is False
    assert comparison.inherent_decision == "Needs Review"
    assert comparison.residual_decision is None
    assert comparison.diverged is None
    assert comparison.divergence_type is DualPrivacyDivergenceType.UNAVAILABLE
    assert "foreign run_id 'run-y'" in comparison.unavailable_inputs[0]


def test_missing_residual_provenance_makes_comparison_unavailable() -> None:
    comparison = compare_dual_privacy_policy(
        _evidence(),
        inherent_privacy_risk_score=86,
        residual_privacy_risk_score=53,
        inherent_provenance=_provenance(),
        residual_provenance=None,
        current_run_id="run-x",
    )

    assert comparison.evaluated is False
    assert comparison.divergence_type is DualPrivacyDivergenceType.UNAVAILABLE
    assert comparison.unavailable_inputs == (
        "residual_privacy_risk_score: missing provenance",
    )


def test_policy_calls_vary_only_privacy_score(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []
    original = publication_gate.evaluate_publication_readiness

    def recording_policy(**kwargs: Any):
        calls.append(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(publication_gate, "evaluate_publication_readiness", recording_policy)

    comparison = _compare(86, 53)

    assert comparison.evaluated is True
    assert len(calls) == 2
    assert calls[0]["privacy_risk_score"] == 86
    assert calls[1]["privacy_risk_score"] == 53
    assert {
        key: value for key, value in calls[0].items() if key != "privacy_risk_score"
    } == {
        key: value for key, value in calls[1].items() if key != "privacy_risk_score"
    }


def test_comparison_is_frozen() -> None:
    comparison = _compare(86, 53)

    with pytest.raises(FrozenInstanceError):
        comparison.run_id = "run-y"  # type: ignore[misc]
