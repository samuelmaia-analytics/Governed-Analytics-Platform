from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

import src.run_platform_pipeline as pipeline
from src.monitoring_components.models import MonitoringCheckResult
from src.observability_components.models import ObservabilityCheck
from src.publication_provenance import (
    EvidenceProvenance,
    EvidenceSource,
    PipelineGovernanceContext,
)
from src.publication_shadow import DualPrivacyDivergenceType
from src.publish_components.models import PrivacyCheck
from src.quality_components.models import QualityCheckResult
from src.schema_contract_components.models import ContractCheck

STARTED_AT = datetime(2026, 8, 14, 12, 30, tzinfo=UTC)


def _context(*, complete: bool = True) -> PipelineGovernanceContext:
    governance = PipelineGovernanceContext("run-x", started_at=STARTED_AT)
    if not complete:
        return governance
    governance.record_quality(
        [QualityCheckResult("quality", "PASS", 0, 0, "high", "ok")]
    )
    governance.record_schema(
        [ContractCheck("dataset", "gold", "schema", "PASS", "ok")]
    )
    governance.record_privacy(
        [PrivacyCheck("privacy", "PASS", "ok")],
        privacy_risk_result={"score": 86},
    )
    governance.residual_privacy_risk_score = 53
    governance.residual_privacy_risk_provenance = EvidenceProvenance(
        EvidenceSource.PRIVACY, "run-x"
    )
    governance.record_classification(
        pd.DataFrame(
            {
                "lgpd_classification": ["sensitive_personal_data"],
                "recommended_action": ["remove"],
            }
        )
    )
    return governance


def _isolate_monitor(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    monitoring = [
        MonitoringCheckResult(
            "published_file_freshness_hours", "PASS", 1, 36, "high", "ok"
        )
    ]
    observability = [
        ObservabilityCheck("freshness", "PASS", "low", 0, 0, "ok")
    ]
    historical_payload: dict[str, object] = {}
    monkeypatch.setattr(pipeline, "run_monitoring", lambda: monitoring)
    monkeypatch.setattr(pipeline, "save_published_monitoring_results", lambda _x: None)
    monkeypatch.setattr(pipeline, "save_published_monitoring_report", lambda _x: None)
    monkeypatch.setattr(
        pipeline, "load_published_monitoring_frame", lambda: pd.DataFrame()
    )
    monkeypatch.setattr(
        pipeline,
        "load_governance_history",
        lambda: pd.DataFrame(
            {"data_quality_score": [73], "privacy_risk_score": [88]}
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "evaluate_governance_observability",
        lambda **_kwargs: observability,
    )
    monkeypatch.setattr(pipeline, "save_observability_results", lambda _x: None)
    monkeypatch.setattr(
        pipeline,
        "save_publication_decision_artifact",
        lambda **kwargs: historical_payload.update(kwargs),
    )
    return historical_payload


def _assert_historical_payload(
    payload: dict[str, object], *, expected_privacy_risk: int = 88
) -> None:
    assert set(payload) == {
        "dataset_name",
        "publication_status",
        "data_quality_score",
        "privacy_risk_score",
        "failed_checks_count",
        "timestamp_utc",
    }
    assert payload["dataset_name"] == "fact_orders_dashboard"
    assert payload["publication_status"] == "Approved"
    assert payload["data_quality_score"] == 73
    assert payload["privacy_risk_score"] == expected_privacy_risk
    assert payload["failed_checks_count"] == 0
    assert {
        "run_id",
        "inherent_decision",
        "residual_decision",
        "divergence_type",
    }.isdisjoint(payload)


def test_default_does_not_call_writer_or_create_dual_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = _isolate_monitor(monkeypatch)
    output_path = tmp_path / "dual.jsonl"
    monkeypatch.setattr(
        pipeline,
        "append_dual_privacy_comparison",
        lambda *args, **kwargs: pytest.fail("dual writer called by default"),
    )

    pipeline._run_monitor_step(
        _context(), dual_privacy_telemetry_path=output_path
    )

    assert not output_path.exists()
    _assert_historical_payload(payload)


def test_opt_in_calls_writer_once_with_run_timestamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = _isolate_monitor(monkeypatch)
    calls: list[tuple[object, datetime, Path]] = []
    output_path = tmp_path / "dual.jsonl"

    def append(comparison, *, timestamp_utc, output_path):
        calls.append((comparison, timestamp_utc, output_path))

    monkeypatch.setattr(pipeline, "append_dual_privacy_comparison", append)

    pipeline._run_monitor_step(
        _context(),
        record_dual_privacy_telemetry=True,
        dual_privacy_telemetry_path=output_path,
    )

    assert len(calls) == 1
    comparison, timestamp, received_path = calls[0]
    assert comparison.run_id == "run-x"
    assert comparison.evaluated is True
    assert comparison.inherent_decision == "Needs Review"
    assert comparison.residual_decision == "Approved"
    assert (
        comparison.divergence_type
        is DualPrivacyDivergenceType.RESIDUAL_LESS_RESTRICTIVE
    )
    assert timestamp == STARTED_AT
    assert received_path == output_path
    _assert_historical_payload(payload)


def test_opt_in_allows_unavailable_comparison(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = _isolate_monitor(monkeypatch)
    captured = []
    monkeypatch.setattr(
        pipeline,
        "append_dual_privacy_comparison",
        lambda comparison, **_kwargs: captured.append(comparison),
    )

    pipeline._run_monitor_step(
        _context(complete=False),
        record_dual_privacy_telemetry=True,
        dual_privacy_telemetry_path=tmp_path / "dual.jsonl",
    )

    assert len(captured) == 1
    assert captured[0].evaluated is False
    assert captured[0].divergence_type is DualPrivacyDivergenceType.UNAVAILABLE
    assert captured[0].unavailable_inputs
    _assert_historical_payload(payload, expected_privacy_risk=88)


def test_dual_writer_failure_is_best_effort_and_independent_from_shadow(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = _isolate_monitor(monkeypatch)
    shadow_calls = []
    monkeypatch.setattr(
        pipeline,
        "append_shadow_comparison",
        lambda comparison, **_kwargs: shadow_calls.append(comparison),
    )

    def fail(*_args, **_kwargs):
        raise OSError("dual diagnostic storage unavailable")

    monkeypatch.setattr(pipeline, "append_dual_privacy_comparison", fail)

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            _context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=tmp_path / "shadow.jsonl",
            record_dual_privacy_telemetry=True,
            dual_privacy_telemetry_path=tmp_path / "dual.jsonl",
        )

    assert len(shadow_calls) == 1
    assert "Falha ao registrar telemetria dual privacy" in caplog.text
    assert "dual diagnostic storage unavailable" in caplog.text
    _assert_historical_payload(payload)


def test_dual_writer_does_not_touch_existing_shadow_jsonl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = _isolate_monitor(monkeypatch)
    existing_shadow = tmp_path / "publication_shadow_comparisons.jsonl"
    existing_bytes = b'{"existing":"shadow"}\n'
    existing_shadow.write_bytes(existing_bytes)
    dual_output = tmp_path / "dual_privacy_shadow_comparisons.jsonl"

    pipeline._run_monitor_step(
        _context(),
        record_dual_privacy_telemetry=True,
        dual_privacy_telemetry_path=dual_output,
    )

    assert existing_shadow.read_bytes() == existing_bytes
    assert dual_output.exists()
    assert dual_output != existing_shadow
    _assert_historical_payload(payload)


def test_cli_flag_is_independent_explicit_opt_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["run_platform_pipeline", "--record-dual-privacy-telemetry"],
    )

    args = pipeline.parse_args()

    assert args.record_dual_privacy_telemetry is True
    assert args.record_shadow_telemetry is False
