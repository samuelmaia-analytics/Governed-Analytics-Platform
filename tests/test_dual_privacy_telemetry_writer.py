from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.publication_shadow.dual_privacy import (
    DualPrivacyDivergenceType,
    DualPrivacyPolicyComparison,
)
from src.publication_shadow.dual_privacy_telemetry import (
    DEFAULT_DUAL_PRIVACY_TELEMETRY_PATH,
    DUAL_PRIVACY_COMPARISON_ID,
    DUAL_PRIVACY_POLICY_ID,
    DUAL_PRIVACY_POLICY_VERSION,
    append_dual_privacy_comparison,
    serialize_dual_privacy_comparison,
)

TIMESTAMP = datetime(2026, 8, 14, 12, 30, tzinfo=UTC)


def _comparison(
    *,
    run_id: str = "run-a",
    divergence_type: DualPrivacyDivergenceType = (
        DualPrivacyDivergenceType.AGREEMENT
    ),
    inherent_decision: str | None = "Approved",
    residual_decision: str | None = "Approved",
    evaluated: bool = True,
) -> DualPrivacyPolicyComparison:
    return DualPrivacyPolicyComparison(
        run_id=run_id,
        evaluated=evaluated,
        inherent_score=86,
        residual_score=53,
        inherent_decision=inherent_decision,  # type: ignore[arg-type]
        residual_decision=residual_decision,  # type: ignore[arg-type]
        inherent_severity="High" if evaluated else None,
        residual_severity="Low" if evaluated else None,
        diverged=(divergence_type is not DualPrivacyDivergenceType.AGREEMENT)
        if evaluated
        else None,
        divergence_type=divergence_type,
        inherent_reasons=("Razão inerente elevada.",) if evaluated else (),
        residual_reasons=("Mitigação aprovada.",) if evaluated else (),
        unavailable_inputs=()
        if evaluated
        else ("residual_privacy_risk_score: foreign run_id 'run-y'",),
    )


@pytest.mark.parametrize(
    ("kind", "inherent_decision", "residual_decision"),
    [
        (DualPrivacyDivergenceType.AGREEMENT, "Approved", "Approved"),
        (
            DualPrivacyDivergenceType.RESIDUAL_LESS_RESTRICTIVE,
            "Needs Review",
            "Approved",
        ),
        (
            DualPrivacyDivergenceType.RESIDUAL_MORE_RESTRICTIVE,
            "Approved",
            "Needs Review",
        ),
    ],
)
def test_serialize_evaluated_comparison_preserves_schema_and_diagnostics(
    kind: DualPrivacyDivergenceType,
    inherent_decision: str,
    residual_decision: str,
) -> None:
    record = serialize_dual_privacy_comparison(
        _comparison(
            divergence_type=kind,
            inherent_decision=inherent_decision,
            residual_decision=residual_decision,
        ),
        timestamp_utc=TIMESTAMP,
    )

    assert list(record) == [
        "run_id",
        "timestamp_utc",
        "policy_id",
        "policy_version",
        "comparison_id",
        "evaluated",
        "inherent_score",
        "residual_score",
        "inherent_decision",
        "residual_decision",
        "inherent_severity",
        "residual_severity",
        "diverged",
        "divergence_type",
        "inherent_reasons",
        "residual_reasons",
        "unavailable_inputs",
    ]
    assert record["run_id"] == "run-a"
    assert record["timestamp_utc"] == "2026-08-14T12:30:00+00:00"
    assert record["policy_id"] == DUAL_PRIVACY_POLICY_ID == "publication_gate"
    assert record["policy_version"] == DUAL_PRIVACY_POLICY_VERSION == "v1"
    assert record["comparison_id"] == (
        DUAL_PRIVACY_COMPARISON_ID
    ) == "inherent_vs_residual_v1"
    assert record["inherent_score"] == 86
    assert record["residual_score"] == 53
    assert record["inherent_decision"] == inherent_decision
    assert record["residual_decision"] == residual_decision
    assert record["divergence_type"] == kind.value
    assert record["inherent_reasons"] == ["Razão inerente elevada."]
    assert record["residual_reasons"] == ["Mitigação aprovada."]


def test_serialize_unavailable_comparison_preserves_diagnostics() -> None:
    record = serialize_dual_privacy_comparison(
        _comparison(
            evaluated=False,
            inherent_decision=None,
            residual_decision=None,
            divergence_type=DualPrivacyDivergenceType.UNAVAILABLE,
        ),
        timestamp_utc=TIMESTAMP,
    )

    assert record["evaluated"] is False
    assert record["inherent_decision"] is None
    assert record["residual_decision"] is None
    assert record["diverged"] is None
    assert record["divergence_type"] == "unavailable"
    assert record["unavailable_inputs"] == [
        "residual_privacy_risk_score: foreign run_id 'run-y'"
    ]


def test_append_is_jsonl_utf8_and_preserves_run_order(tmp_path: Path) -> None:
    output_path = tmp_path / "monitoring" / "dual.jsonl"

    assert append_dual_privacy_comparison(
        _comparison(run_id="run-a"),
        timestamp_utc=TIMESTAMP,
        output_path=output_path,
    ) == output_path
    append_dual_privacy_comparison(
        _comparison(
            run_id="run-b",
            divergence_type=(
                DualPrivacyDivergenceType.RESIDUAL_LESS_RESTRICTIVE
            ),
            inherent_decision="Needs Review",
        ),
        timestamp_utc=TIMESTAMP,
        output_path=output_path,
    )

    raw = output_path.read_text(encoding="utf-8")
    records = [json.loads(line) for line in raw.splitlines()]
    assert [record["run_id"] for record in records] == ["run-a", "run-b"]
    assert "Razão inerente elevada." in raw
    assert len(records) == 2


def test_writer_requires_aware_timestamp_and_propagates_path_errors(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        append_dual_privacy_comparison(
            _comparison(),
            timestamp_utc=datetime(2026, 8, 14, 12, 30),
            output_path=tmp_path / "dual.jsonl",
        )

    occupied_parent = tmp_path / "occupied"
    occupied_parent.write_text("file", encoding="utf-8")
    with pytest.raises(OSError):
        append_dual_privacy_comparison(
            _comparison(),
            timestamp_utc=TIMESTAMP,
            output_path=occupied_parent / "dual.jsonl",
        )


def test_default_path_is_separate_from_existing_governance_artifacts() -> None:
    assert DEFAULT_DUAL_PRIVACY_TELEMETRY_PATH.as_posix().endswith(
        "data/published/monitoring/dual_privacy_shadow_comparisons.jsonl"
    )
    assert DEFAULT_DUAL_PRIVACY_TELEMETRY_PATH.name not in {
        "publication_decision.json",
        "publication_shadow_comparisons.jsonl",
        "governance_history.csv",
    }
