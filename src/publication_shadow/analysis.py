from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from src.publication_gate import PublicationDecision, PublicationSeverity
from src.publication_shadow.comparison import ShadowDivergenceType
from src.publication_shadow.evaluation import CurrentMonitorDecision


@dataclass(frozen=True)
class PersistedShadowTelemetryRecord:
    run_id: str
    timestamp_utc: datetime
    policy_id: str
    policy_version: str
    historical_policy_id: str
    evaluated: bool
    historical_decision: CurrentMonitorDecision
    canonical_decision: PublicationDecision | None
    diverged: bool | None
    divergence_type: ShadowDivergenceType
    canonical_severity: PublicationSeverity | None
    canonical_reasons: tuple[str, ...]
    canonical_required_actions: tuple[str, ...]
    provenance_valid: bool
    current_sources: tuple[str, ...]
    missing_sources: tuple[str, ...]
    foreign_run_sources: tuple[str, ...]
    unknown_sources: tuple[str, ...]
    unavailable_inputs: tuple[str, ...]


@dataclass(frozen=True)
class ShadowTelemetryMetrics:
    total_runs: int
    evaluated: int
    unavailable: int
    evaluation_rate: float
    unavailable_rate: float
    agreements: int
    canonical_stricter: int
    historical_stricter: int
    divergence_count: int
    divergence_rate: float
    canonical_approved: int
    canonical_needs_review: int
    canonical_blocked: int


@dataclass(frozen=True)
class PolicyTelemetrySummary:
    policy_id: str
    policy_version: str
    historical_policy_id: str
    metrics: ShadowTelemetryMetrics


@dataclass(frozen=True)
class ShadowTelemetryAnalysis:
    physical_records: tuple[PersistedShadowTelemetryRecord, ...]
    records: tuple[PersistedShadowTelemetryRecord, ...]
    metrics: ShadowTelemetryMetrics
    unavailable_reasons: tuple[tuple[str, int], ...]
    missing_sources: tuple[tuple[str, int], ...]
    foreign_run_sources: tuple[tuple[str, int], ...]
    unknown_sources: tuple[tuple[str, int], ...]
    policy_groups: tuple[PolicyTelemetrySummary, ...]
    duplicated_run_ids: tuple[str, ...]
    records_per_run: tuple[tuple[str, int], ...]
    canonical_blocked_runs: tuple[PersistedShadowTelemetryRecord, ...]
    first_record: PersistedShadowTelemetryRecord | None
    last_record: PersistedShadowTelemetryRecord | None
    observed_from: datetime | None
    observed_to: datetime | None


def _required(record: Mapping[str, Any], field: str) -> Any:
    if field not in record:
        raise ValueError(f"missing required field {field!r}")
    return record[field]


def _string(record: Mapping[str, Any], field: str) -> str:
    value = _required(record, field)
    if not isinstance(value, str):
        raise ValueError(f"field {field!r} must be a string")
    return value


def _optional_string(record: Mapping[str, Any], field: str) -> str | None:
    value = _required(record, field)
    if value is not None and not isinstance(value, str):
        raise ValueError(f"field {field!r} must be a string or null")
    return value


def _boolean(record: Mapping[str, Any], field: str) -> bool:
    value = _required(record, field)
    if not isinstance(value, bool):
        raise ValueError(f"field {field!r} must be a boolean")
    return value


def _optional_boolean(record: Mapping[str, Any], field: str) -> bool | None:
    value = _required(record, field)
    if value is not None and not isinstance(value, bool):
        raise ValueError(f"field {field!r} must be a boolean or null")
    return value


def _strings(record: Mapping[str, Any], field: str) -> tuple[str, ...]:
    value = _required(record, field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"field {field!r} must be a list of strings")
    return tuple(value)


def _timestamp(record: Mapping[str, Any]) -> datetime:
    raw = _string(record, "timestamp_utc")
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("field 'timestamp_utc' must be an ISO-8601 timestamp") from exc
    if value.utcoffset() is None:
        raise ValueError("field 'timestamp_utc' must be timezone-aware")
    return value


def _parse_record(record: object) -> PersistedShadowTelemetryRecord:
    if not isinstance(record, dict):
        raise ValueError("telemetry record must be a JSON object")
    data = cast(Mapping[str, Any], record)
    historical = _string(data, "historical_decision")
    if historical not in {"Approved", "Needs Review"}:
        raise ValueError("field 'historical_decision' has an unsupported value")
    canonical = _optional_string(data, "canonical_decision")
    if canonical not in {None, "Approved", "Needs Review", "Blocked"}:
        raise ValueError("field 'canonical_decision' has an unsupported value")
    severity = _optional_string(data, "canonical_severity")
    if severity not in {None, "Low", "Medium", "High", "Critical"}:
        raise ValueError("field 'canonical_severity' has an unsupported value")
    divergence = _string(data, "divergence_type")
    try:
        divergence_type = ShadowDivergenceType(divergence)
    except ValueError as exc:
        raise ValueError("field 'divergence_type' has an unsupported value") from exc
    return PersistedShadowTelemetryRecord(
        run_id=_string(data, "run_id"),
        timestamp_utc=_timestamp(data),
        policy_id=_string(data, "policy_id"),
        policy_version=_string(data, "policy_version"),
        historical_policy_id=_string(data, "historical_policy_id"),
        evaluated=_boolean(data, "evaluated"),
        historical_decision=cast(CurrentMonitorDecision, historical),
        canonical_decision=cast(PublicationDecision | None, canonical),
        diverged=_optional_boolean(data, "diverged"),
        divergence_type=divergence_type,
        canonical_severity=cast(PublicationSeverity | None, severity),
        canonical_reasons=_strings(data, "canonical_reasons"),
        canonical_required_actions=_strings(data, "canonical_required_actions"),
        provenance_valid=_boolean(data, "provenance_valid"),
        current_sources=_strings(data, "current_sources"),
        missing_sources=_strings(data, "missing_sources"),
        foreign_run_sources=_strings(data, "foreign_run_sources"),
        unknown_sources=_strings(data, "unknown_sources"),
        unavailable_inputs=_strings(data, "unavailable_inputs"),
    )


def load_shadow_telemetry(path: str | Path) -> tuple[PersistedShadowTelemetryRecord, ...]:
    telemetry_path = Path(path)
    if not telemetry_path.exists():
        return ()
    records: list[PersistedShadowTelemetryRecord] = []
    for line_number, line in enumerate(
        telemetry_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            records.append(_parse_record(json.loads(line)))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(
                f"Invalid shadow telemetry at {telemetry_path}, line {line_number}: {exc}"
            ) from exc
    return tuple(records)


def _rate(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100, 2) if denominator else 0.0


def _metrics(records: Sequence[PersistedShadowTelemetryRecord]) -> ShadowTelemetryMetrics:
    evaluated = sum(record.evaluated for record in records)
    unavailable = len(records) - evaluated
    agreements = sum(
        record.divergence_type is ShadowDivergenceType.AGREEMENT for record in records
    )
    canonical_stricter = sum(
        record.divergence_type is ShadowDivergenceType.CANONICAL_STRICTER
        for record in records
    )
    historical_stricter = sum(
        record.divergence_type is ShadowDivergenceType.HISTORICAL_STRICTER
        for record in records
    )
    divergences = canonical_stricter + historical_stricter
    return ShadowTelemetryMetrics(
        total_runs=len(records),
        evaluated=evaluated,
        unavailable=unavailable,
        evaluation_rate=_rate(evaluated, len(records)),
        unavailable_rate=_rate(unavailable, len(records)),
        agreements=agreements,
        canonical_stricter=canonical_stricter,
        historical_stricter=historical_stricter,
        divergence_count=divergences,
        divergence_rate=_rate(divergences, evaluated),
        canonical_approved=sum(
            record.canonical_decision == "Approved" for record in records
        ),
        canonical_needs_review=sum(
            record.canonical_decision == "Needs Review" for record in records
        ),
        canonical_blocked=sum(
            record.canonical_decision == "Blocked" for record in records
        ),
    )


def _counts(values: Sequence[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(values).items()))


def analyze_shadow_telemetry(
    records: Sequence[PersistedShadowTelemetryRecord],
    *,
    sort_by_timestamp: bool = False,
) -> ShadowTelemetryAnalysis:
    physical_records = tuple(records)
    analyzed_records = (
        tuple(sorted(physical_records, key=lambda record: record.timestamp_utc))
        if sort_by_timestamp
        else physical_records
    )
    policy_records: dict[tuple[str, str, str], list[PersistedShadowTelemetryRecord]] = {}
    for record in physical_records:
        key = (record.policy_id, record.policy_version, record.historical_policy_id)
        policy_records.setdefault(key, []).append(record)
    policy_groups = tuple(
        PolicyTelemetrySummary(*key, _metrics(group))
        for key, group in sorted(policy_records.items())
    )
    run_counts = Counter(record.run_id for record in physical_records)
    timestamps = [record.timestamp_utc for record in physical_records]
    return ShadowTelemetryAnalysis(
        physical_records=physical_records,
        records=analyzed_records,
        metrics=_metrics(physical_records),
        unavailable_reasons=_counts(
            [value for record in physical_records for value in record.unavailable_inputs]
        ),
        missing_sources=_counts(
            [value for record in physical_records for value in record.missing_sources]
        ),
        foreign_run_sources=_counts(
            [value for record in physical_records for value in record.foreign_run_sources]
        ),
        unknown_sources=_counts(
            [value for record in physical_records for value in record.unknown_sources]
        ),
        policy_groups=policy_groups,
        duplicated_run_ids=tuple(sorted(run_id for run_id, count in run_counts.items() if count > 1)),
        records_per_run=tuple(sorted(run_counts.items())),
        canonical_blocked_runs=tuple(
            record for record in physical_records if record.canonical_decision == "Blocked"
        ),
        first_record=analyzed_records[0] if analyzed_records else None,
        last_record=analyzed_records[-1] if analyzed_records else None,
        observed_from=min(timestamps) if timestamps else None,
        observed_to=max(timestamps) if timestamps else None,
    )
