from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.publication_provenance.models import EvidenceSource
from src.publication_shadow.comparison import (
    PublicationShadowComparison,
    ShadowDivergenceType,
)
from src.publication_shadow.telemetry import (
    DEFAULT_SHADOW_TELEMETRY_PATH,
    HISTORICAL_POLICY_ID,
    SHADOW_POLICY_ID,
    SHADOW_POLICY_VERSION,
    append_shadow_comparison,
    serialize_shadow_comparison,
)

TIMESTAMP = datetime(2026, 8, 13, 12, 30, tzinfo=UTC)


def comparison(
    *,
    run_id: str = "run-a",
    divergence_type: ShadowDivergenceType = ShadowDivergenceType.AGREEMENT,
    historical: str = "Approved",
    canonical: str | None = "Approved",
    evaluated: bool = True,
) -> PublicationShadowComparison:
    return PublicationShadowComparison(
        run_id=run_id,
        evaluated=evaluated,
        current_monitor_decision=historical,  # type: ignore[arg-type]
        canonical_decision=canonical,  # type: ignore[arg-type]
        diverged=(divergence_type is not ShadowDivergenceType.AGREEMENT)
        if evaluated
        else None,
        divergence_type=divergence_type,
        canonical_severity="Medium" if evaluated else None,
        canonical_reasons=("Ação canônica necessária.",) if evaluated else (),
        canonical_required_actions=("Revisar controles.",) if evaluated else (),
        provenance_valid=evaluated,
        current_sources=(EvidenceSource.MONITORING,) if evaluated else (),
        missing_sources=()
        if evaluated
        else (EvidenceSource.OPERATIONAL_QUALITY,),
        foreign_run_sources=(),
        unknown_sources=(),
        unavailable_inputs=() if evaluated else ("operational_quality: missing",),
    )


@pytest.mark.parametrize(
    ("kind", "historical", "canonical"),
    [
        (ShadowDivergenceType.AGREEMENT, "Approved", "Approved"),
        (ShadowDivergenceType.CANONICAL_STRICTER, "Approved", "Blocked"),
        (ShadowDivergenceType.HISTORICAL_STRICTER, "Needs Review", "Approved"),
    ],
)
def test_serialize_evaluated_comparison_preserves_diagnostics(
    kind: ShadowDivergenceType, historical: str, canonical: str
) -> None:
    record = serialize_shadow_comparison(
        comparison(
            divergence_type=kind,
            historical=historical,
            canonical=canonical,
        ),
        timestamp_utc=TIMESTAMP,
    )

    assert record["run_id"] == "run-a"
    assert record["timestamp_utc"] == "2026-08-13T12:30:00+00:00"
    assert record["policy_id"] == SHADOW_POLICY_ID == "publication_gate"
    assert record["policy_version"] == SHADOW_POLICY_VERSION == "v1"
    assert record["historical_policy_id"] == (
        HISTORICAL_POLICY_ID
    ) == "published_monitoring_binary_v1"
    assert record["historical_decision"] == historical
    assert record["canonical_decision"] == canonical
    assert record["divergence_type"] == kind.value
    assert record["canonical_reasons"] == ["Ação canônica necessária."]
    assert record["canonical_required_actions"] == ["Revisar controles."]
    assert record["current_sources"] == ["monitoring"]


def test_serialize_unavailable_keeps_provenance_diagnostics() -> None:
    record = serialize_shadow_comparison(
        comparison(
            evaluated=False,
            canonical=None,
            divergence_type=ShadowDivergenceType.UNAVAILABLE,
        ),
        timestamp_utc=TIMESTAMP,
    )

    assert record["evaluated"] is False
    assert record["canonical_decision"] is None
    assert record["diverged"] is None
    assert record["divergence_type"] == "unavailable"
    assert record["missing_sources"] == ["operational_quality"]
    assert record["unavailable_inputs"] == ["operational_quality: missing"]


def test_append_is_jsonl_utf8_and_preserves_run_order(tmp_path: Path) -> None:
    output_path = tmp_path / "monitoring" / "shadow.jsonl"

    assert append_shadow_comparison(
        comparison(run_id="run-a"),
        timestamp_utc=TIMESTAMP,
        output_path=output_path,
    ) == output_path
    append_shadow_comparison(
        comparison(
            run_id="run-b",
            divergence_type=ShadowDivergenceType.CANONICAL_STRICTER,
            canonical="Blocked",
        ),
        timestamp_utc=TIMESTAMP,
        output_path=output_path,
    )

    raw = output_path.read_text(encoding="utf-8")
    records = [json.loads(line) for line in raw.splitlines()]
    assert [record["run_id"] for record in records] == ["run-a", "run-b"]
    assert "Ação canônica necessária." in raw
    assert len(records) == 2


def test_writer_requires_aware_timestamp_and_propagates_path_errors(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        append_shadow_comparison(
            comparison(),
            timestamp_utc=datetime(2026, 8, 13, 12, 30),
            output_path=tmp_path / "shadow.jsonl",
        )

    occupied_parent = tmp_path / "occupied"
    occupied_parent.write_text("file", encoding="utf-8")
    with pytest.raises(OSError):
        append_shadow_comparison(
            comparison(),
            timestamp_utc=TIMESTAMP,
            output_path=occupied_parent / "shadow.jsonl",
        )


def test_default_path_is_new_and_separate_from_authoritative_artifacts() -> None:
    assert DEFAULT_SHADOW_TELEMETRY_PATH.as_posix().endswith(
        "data/published/monitoring/publication_shadow_comparisons.jsonl"
    )
    assert DEFAULT_SHADOW_TELEMETRY_PATH.name != "publication_decision.json"
    assert DEFAULT_SHADOW_TELEMETRY_PATH.name != "governance_history.csv"
