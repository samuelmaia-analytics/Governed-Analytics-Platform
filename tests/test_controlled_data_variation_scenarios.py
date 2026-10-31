from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pytest

from src.publication_evidence.models import PublicationEvidence
from src.publication_gate import evaluate_publication_readiness
from src.publication_provenance import (
    DatasetContentComparison,
    DatasetContentProvenance,
    EvidenceProvenance,
    EvidenceSource,
    build_dataset_content_provenance,
    compare_dataset_content_provenance,
)
from src.publication_shadow import (
    DualPrivacyDivergenceType,
    compare_dual_privacy_policy,
    evaluate_dual_privacy_shadow,
)


@dataclass(frozen=True)
class ControlledFrames:
    workspace: Path
    source: pd.DataFrame
    published: pd.DataFrame


@pytest.fixture
def controlled_frames(tmp_path: Path) -> ControlledFrames:
    source = pd.DataFrame(
        {
            "order_id": ["o1", "o2"],
            "order_item_id": [1, 1],
            "product_id": ["p1", "p2"],
            "seller_id": ["s1", "s2"],
            "price": [10.0, 20.0],
        }
    )
    published = pd.DataFrame(
        {
            "order_id": ["order-a", "order-b"],
            "order_item_id": [1, 1],
            "seller_key": ["seller-a", "seller-b"],
            "price": [10.0, 20.0],
        }
    )
    return ControlledFrames(tmp_path, source, published)


def _content_provenance(
    run_id: str,
    source: pd.DataFrame,
    published: pd.DataFrame,
) -> DatasetContentProvenance:
    return build_dataset_content_provenance(
        run_id=run_id,
        source=source,
        published=published,
    )


def _evidence(
    *,
    quality_score: int = 100,
    schema_status: str = "PASS",
    protected: bool = True,
) -> PublicationEvidence:
    return PublicationEvidence(
        quality_status="PASS",
        quality_score=quality_score,
        quality_failed_checks=0,
        quality_warning_checks=0,
        critical_quality_failures=0,
        schema_status=schema_status,  # type: ignore[arg-type]
        business_rules_status="PASS",
        business_rule_failed_checks=0,
        privacy_risk_score=0,
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


def _privacy_provenance(run_id: str = "run-current") -> EvidenceProvenance:
    return EvidenceProvenance(EvidenceSource.PRIVACY, run_id)


def _dual_comparison(
    inherent_score: int,
    residual_score: int,
    *,
    evidence: PublicationEvidence | None = None,
):
    return compare_dual_privacy_policy(
        evidence or _evidence(),
        inherent_privacy_risk_score=inherent_score,
        residual_privacy_risk_score=residual_score,
        inherent_provenance=_privacy_provenance(),
        residual_provenance=_privacy_provenance(),
        current_run_id="run-current",
    )


def test_same_content_preserves_the_simulated_baseline_decisions(
    controlled_frames: ControlledFrames,
) -> None:
    assert controlled_frames.workspace.is_dir()
    first = _content_provenance(
        "run-a",
        controlled_frames.source,
        controlled_frames.published,
    )
    second = _content_provenance(
        "run-b",
        controlled_frames.source.copy(deep=True),
        controlled_frames.published.copy(deep=True),
    )
    baseline = _dual_comparison(86, 53)
    repeated = _dual_comparison(86, 53)

    assert (
        compare_dataset_content_provenance(first, second)
        is DatasetContentComparison.SAME_CONTENT
    )
    assert (baseline.inherent_decision, baseline.residual_decision) == (
        repeated.inherent_decision,
        repeated.residual_decision,
    )


@pytest.mark.parametrize(
    ("change_source", "change_published", "expected"),
    [
        (True, False, DatasetContentComparison.SOURCE_CHANGED),
        (False, True, DatasetContentComparison.PUBLISHED_CHANGED),
        (True, True, DatasetContentComparison.BOTH_CHANGED),
    ],
    ids=["source-changed", "published-changed", "both-changed"],
)
def test_controlled_content_changes_are_classified(
    controlled_frames: ControlledFrames,
    change_source: bool,
    change_published: bool,
    expected: DatasetContentComparison,
) -> None:
    baseline = _content_provenance(
        "run-a",
        controlled_frames.source,
        controlled_frames.published,
    )
    source = controlled_frames.source.copy(deep=True)
    published = controlled_frames.published.copy(deep=True)
    if change_source:
        source.loc[0, "price"] = 11.0
    if change_published:
        published.loc[0, "price"] = 11.0
    changed = _content_provenance("run-b", source, published)

    assert compare_dataset_content_provenance(baseline, changed) is expected


@pytest.mark.parametrize(
    (
        "inherent_score",
        "residual_score",
        "inherent_decision",
        "residual_decision",
        "divergence_type",
    ),
    [
        (
            86,
            53,
            "Needs Review",
            "Approved",
            DualPrivacyDivergenceType.RESIDUAL_LESS_RESTRICTIVE,
        ),
        (50, 40, "Approved", "Approved", DualPrivacyDivergenceType.AGREEMENT),
        (
            86,
            70,
            "Needs Review",
            "Needs Review",
            DualPrivacyDivergenceType.AGREEMENT,
        ),
        (
            53,
            86,
            "Approved",
            "Needs Review",
            DualPrivacyDivergenceType.RESIDUAL_MORE_RESTRICTIVE,
        ),
    ],
    ids=[
        "residual-less-restrictive",
        "agreement-approved",
        "agreement-needs-review",
        "residual-more-restrictive",
    ],
)
def test_controlled_scores_use_the_existing_dual_policy(
    inherent_score: int,
    residual_score: int,
    inherent_decision: str,
    residual_decision: str,
    divergence_type: DualPrivacyDivergenceType,
) -> None:
    evidence = _evidence()
    evaluation = evaluate_dual_privacy_shadow(
        evidence,
        inherent_privacy_risk_score=inherent_score,
        residual_privacy_risk_score=residual_score,
        inherent_provenance=_privacy_provenance(),
        residual_provenance=_privacy_provenance(),
        current_run_id="run-current",
        current_monitor_decision="Approved",
    )
    comparison = _dual_comparison(
        inherent_score,
        residual_score,
        evidence=evidence,
    )

    assert evaluation.inherent.canonical_decision is not None
    assert evaluation.residual.canonical_decision is not None
    assert evaluation.inherent.canonical_decision.decision == inherent_decision
    assert evaluation.residual.canonical_decision.decision == residual_decision
    assert comparison.inherent_decision == inherent_decision
    assert comparison.residual_decision == residual_decision
    assert comparison.divergence_type is divergence_type


def test_unprotected_sensitive_data_blocks_both_policy_branches() -> None:
    comparison = _dual_comparison(86, 53, evidence=_evidence(protected=False))

    assert comparison.inherent_decision == "Blocked"
    assert comparison.residual_decision == "Blocked"
    assert comparison.inherent_severity == "Critical"
    assert comparison.residual_severity == "Critical"
    assert comparison.divergence_type is DualPrivacyDivergenceType.AGREEMENT


@pytest.mark.parametrize(
    "residual_provenance",
    [None, _privacy_provenance("run-foreign")],
    ids=["missing", "foreign-run"],
)
def test_missing_or_foreign_provenance_is_unavailable(
    residual_provenance: EvidenceProvenance | None,
) -> None:
    comparison = compare_dual_privacy_policy(
        _evidence(),
        inherent_privacy_risk_score=86,
        residual_privacy_risk_score=53,
        inherent_provenance=_privacy_provenance(),
        residual_provenance=residual_provenance,
        current_run_id="run-current",
    )

    assert comparison.evaluated is False
    assert comparison.divergence_type is DualPrivacyDivergenceType.UNAVAILABLE
    assert comparison.unavailable_inputs


def test_degraded_quality_uses_the_current_policy_without_threshold_changes() -> None:
    direct = evaluate_publication_readiness(
        data_quality_score=79,
        privacy_risk_score=40,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    comparison = _dual_comparison(
        50,
        40,
        evidence=_evidence(quality_score=79),
    )

    assert direct.decision == "Needs Review"
    assert direct.severity == "Medium"
    assert comparison.inherent_decision == "Needs Review"
    assert comparison.residual_decision == "Needs Review"
    assert comparison.divergence_type is DualPrivacyDivergenceType.AGREEMENT


def test_schema_failure_uses_the_current_policy_and_blocks_both_branches() -> None:
    direct = evaluate_publication_readiness(
        data_quality_score=100,
        privacy_risk_score=40,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="failed",
        has_sensitive_data_without_protection=False,
    )
    comparison = _dual_comparison(
        50,
        40,
        evidence=_evidence(schema_status="FAIL"),
    )

    assert direct.decision == "Blocked"
    assert direct.severity == "Critical"
    assert comparison.inherent_decision == "Blocked"
    assert comparison.residual_decision == "Blocked"
    assert comparison.divergence_type is DualPrivacyDivergenceType.AGREEMENT
