from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from src.publication_shadow.analysis import (
    analyze_shadow_telemetry,
    load_shadow_telemetry,
)


def _record(
    run_id: str,
    *,
    minute: int,
    divergence_type: str = "agreement",
    evaluated: bool = True,
    canonical_decision: str | None = "Approved",
    policy_version: str = "v1",
    unavailable_inputs: list[str] | None = None,
    missing_sources: list[str] | None = None,
    foreign_run_sources: list[str] | None = None,
    unknown_sources: list[str] | None = None,
) -> dict[str, object]:
    diverged = None if not evaluated else divergence_type != "agreement"
    return {
        "run_id": run_id,
        "timestamp_utc": (datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=minute)).isoformat(),
        "policy_id": "publication_gate",
        "policy_version": policy_version,
        "historical_policy_id": "published_monitoring_binary_v1",
        "evaluated": evaluated,
        "historical_decision": "Approved",
        "canonical_decision": canonical_decision,
        "diverged": diverged,
        "divergence_type": divergence_type,
        "canonical_severity": "Critical" if canonical_decision == "Blocked" else ("Low" if evaluated else None),
        "canonical_reasons": ["reason"] if evaluated else [],
        "canonical_required_actions": ["action"] if evaluated else [],
        "provenance_valid": evaluated,
        "current_sources": ["monitoring"] if evaluated else [],
        "missing_sources": missing_sources or [],
        "foreign_run_sources": foreign_run_sources or [],
        "unknown_sources": unknown_sources or [],
        "unavailable_inputs": unavailable_inputs or [],
    }


def _write(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def test_missing_and_empty_files_return_empty_collections(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")

    assert load_shadow_telemetry(missing) == ()
    assert load_shadow_telemetry(empty) == ()
    assert analyze_shadow_telemetry(()).metrics.total_runs == 0


def test_loader_preserves_physical_order_and_parses_aware_timestamps(tmp_path: Path) -> None:
    path = tmp_path / "telemetry.jsonl"
    _write(path, [_record("run-later", minute=2), _record("run-earlier", minute=1)])

    records = load_shadow_telemetry(path)
    physical = analyze_shadow_telemetry(records)
    chronological = analyze_shadow_telemetry(records, sort_by_timestamp=True)

    assert [record.run_id for record in records] == ["run-later", "run-earlier"]
    assert physical.first_record is not None
    assert physical.first_record.run_id == "run-later"
    assert chronological.first_record is not None
    assert chronological.first_record.run_id == "run-earlier"
    assert records[0].timestamp_utc.utcoffset() is not None


@pytest.mark.parametrize(
    "line",
    ["not-json", json.dumps({"run_id": "incomplete"})],
)
def test_invalid_line_raises_clear_error(tmp_path: Path, line: str) -> None:
    path = tmp_path / "invalid.jsonl"
    path.write_text(line + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"Invalid shadow telemetry.*line 1"):
        load_shadow_telemetry(path)


def test_operational_fixture_calculates_rates_and_divergence_types(tmp_path: Path) -> None:
    path = tmp_path / "telemetry.jsonl"
    records = [
        *[_record(f"agreement-{index}", minute=index) for index in range(4)],
        _record("canonical", minute=4, divergence_type="canonical_stricter", canonical_decision="Needs Review"),
        _record("historical", minute=5, divergence_type="historical_stricter"),
        *[
            _record(
                f"unavailable-{index}",
                minute=6 + index,
                divergence_type="unavailable",
                evaluated=False,
                canonical_decision=None,
                unavailable_inputs=["quality_score", "privacy_risk_score"],
                missing_sources=["operational_quality"],
            )
            for index in range(4)
        ],
    ]
    _write(path, records)

    metrics = analyze_shadow_telemetry(load_shadow_telemetry(path)).metrics

    assert metrics.total_runs == 10
    assert metrics.evaluated == 6
    assert metrics.unavailable == 4
    assert metrics.evaluation_rate == 60.0
    assert metrics.unavailable_rate == 40.0
    assert metrics.agreements == 4
    assert metrics.canonical_stricter == 1
    assert metrics.historical_stricter == 1
    assert metrics.divergence_count == 2
    assert metrics.divergence_rate == 33.33


def test_unavailable_diagnostics_preserve_actual_values(tmp_path: Path) -> None:
    path = tmp_path / "telemetry.jsonl"
    _write(
        path,
        [
            _record(
                "missing",
                minute=0,
                divergence_type="unavailable",
                evaluated=False,
                canonical_decision=None,
                unavailable_inputs=["quality_score", "custom_input"],
                missing_sources=["privacy"],
                foreign_run_sources=["schema_contracts"],
                unknown_sources=["classification"],
            )
        ],
    )

    analysis = analyze_shadow_telemetry(load_shadow_telemetry(path))

    assert analysis.unavailable_reasons == (("custom_input", 1), ("quality_score", 1))
    assert analysis.missing_sources == (("privacy", 1),)
    assert analysis.foreign_run_sources == (("schema_contracts", 1),)
    assert analysis.unknown_sources == (("classification", 1),)


def test_policy_versions_are_analyzed_separately(tmp_path: Path) -> None:
    path = tmp_path / "telemetry.jsonl"
    _write(
        path,
        [
            _record("v1", minute=0, policy_version="v1"),
            _record(
                "v2",
                minute=1,
                policy_version="v2",
                divergence_type="canonical_stricter",
                canonical_decision="Blocked",
            ),
        ],
    )

    groups = analyze_shadow_telemetry(load_shadow_telemetry(path)).policy_groups

    assert [(group.policy_version, group.metrics.total_runs) for group in groups] == [
        ("v1", 1),
        ("v2", 1),
    ]
    assert groups[0].metrics.divergence_rate == 0.0
    assert groups[1].metrics.divergence_rate == 100.0


def test_duplicate_runs_are_reported_without_deduplication(tmp_path: Path) -> None:
    path = tmp_path / "telemetry.jsonl"
    _write(path, [_record("same", minute=0), _record("same", minute=1)])

    analysis = analyze_shadow_telemetry(load_shadow_telemetry(path))

    assert analysis.metrics.total_runs == 2
    assert analysis.duplicated_run_ids == ("same",)
    assert analysis.records_per_run == (("same", 2),)


def test_canonical_blocked_runs_keep_diagnostic_context(tmp_path: Path) -> None:
    path = tmp_path / "telemetry.jsonl"
    blocked = _record(
        "blocked-run",
        minute=0,
        divergence_type="canonical_stricter",
        canonical_decision="Blocked",
        foreign_run_sources=["schema_contracts"],
    )
    blocked["historical_decision"] = "Needs Review"
    blocked["canonical_reasons"] = ["Schema contract validation failed."]
    _write(path, [blocked, _record("approved", minute=1)])

    analysis = analyze_shadow_telemetry(load_shadow_telemetry(path))
    record = analysis.canonical_blocked_runs[0]

    assert analysis.metrics.canonical_blocked == 1
    assert record.run_id == "blocked-run"
    assert record.historical_decision == "Needs Review"
    assert record.canonical_severity == "Critical"
    assert record.canonical_reasons == ("Schema contract validation failed.",)
    assert record.foreign_run_sources == ("schema_contracts",)
    assert analysis.observed_from == datetime(2026, 1, 1, tzinfo=UTC)
    assert analysis.observed_to == datetime(2026, 1, 1, 0, 1, tzinfo=UTC)
