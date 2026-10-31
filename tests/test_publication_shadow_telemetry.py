from __future__ import annotations

from dataclasses import replace

from src.publication_provenance.models import ProvenanceValidationResult
from src.publication_shadow.comparison import (
    ShadowDivergenceType,
    compare_publication_shadow,
    summarize_shadow_comparisons,
)
from src.publication_shadow.evaluation import ShadowPublicationEvaluation
from tests.test_publication_shadow_comparison import shadow, valid_provenance


def test_summary_uses_only_evaluated_comparisons_for_divergence_rate() -> None:
    evaluated = [
        compare_publication_shadow(shadow("Approved", "Approved"), valid_provenance())
        for _ in range(4)
    ]
    evaluated.extend(
        [
            compare_publication_shadow(
                shadow("Approved", "Needs Review"), valid_provenance()
            ),
            compare_publication_shadow(
                shadow("Needs Review", "Approved"), valid_provenance()
            ),
        ]
    )
    invalid_provenance: ProvenanceValidationResult = replace(
        valid_provenance(), valid=False
    )
    unavailable = compare_publication_shadow(
        ShadowPublicationEvaluation(
            False, None, "Approved", None, ("quality_score",)
        ),
        invalid_provenance,
    )

    summary = summarize_shadow_comparisons(
        [*evaluated, unavailable, unavailable, unavailable, unavailable]
    )

    assert summary.total == 10
    assert summary.evaluated == 6
    assert summary.unavailable == 4
    assert summary.agreements == 4
    assert summary.canonical_stricter == 1
    assert summary.historical_stricter == 1
    assert summary.divergence_rate == 33.33


def test_summary_of_only_unavailable_comparisons_has_zero_rate() -> None:
    comparison = compare_publication_shadow(
        ShadowPublicationEvaluation(False, None, "Approved", None, ("missing",)),
        replace(valid_provenance(), valid=False),
    )

    summary = summarize_shadow_comparisons([comparison])

    assert comparison.divergence_type is ShadowDivergenceType.UNAVAILABLE
    assert summary.evaluated == 0
    assert summary.divergence_rate == 0.0
