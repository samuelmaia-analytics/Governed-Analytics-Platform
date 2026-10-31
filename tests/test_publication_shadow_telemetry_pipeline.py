from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

import src.run_platform_pipeline as pipeline
from src.monitoring_components.models import MonitoringCheckResult
from src.observability_components.models import ObservabilityCheck
from src.publication_provenance import PipelineGovernanceContext
from src.publication_shadow import ShadowDivergenceType
from src.publish_components.models import PrivacyCheck
from src.quality_components.models import QualityCheckResult
from src.schema_contract_components.models import ContractCheck

STARTED_AT = datetime(2026, 8, 13, 12, 30, tzinfo=UTC)


def context(*, complete: bool = True) -> PipelineGovernanceContext:
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
        privacy_risk_result={"score": 20},
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


def isolate_monitor(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    monitoring = [
        MonitoringCheckResult(
            "published_file_freshness_hours", "PASS", 1, 36, "high", "ok"
        )
    ]
    observability = [
        ObservabilityCheck("freshness", "PASS", "low", 0, 0, "ok")
    ]
    writer_payload: dict[str, object] = {}
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
        lambda **kwargs: writer_payload.update(kwargs),
    )
    return writer_payload


def assert_historical_payload(
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
    assert "run_id" not in payload
    assert "canonical_decision" not in payload
    assert "divergence" not in payload


def test_default_monitor_path_never_calls_telemetry_writer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = isolate_monitor(monkeypatch)
    monkeypatch.setattr(
        pipeline,
        "append_shadow_comparison",
        lambda *args, **kwargs: pytest.fail("telemetry writer called by default"),
    )

    pipeline._run_monitor_step(context())

    assert_historical_payload(payload)


def test_opt_in_calls_writer_once_with_run_timestamp_and_explicit_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = isolate_monitor(monkeypatch)
    calls: list[tuple[object, datetime, Path]] = []
    output_path = tmp_path / "shadow.jsonl"

    def append(comparison, *, timestamp_utc, output_path):
        calls.append((comparison, timestamp_utc, output_path))

    monkeypatch.setattr(pipeline, "append_shadow_comparison", append)

    pipeline._run_monitor_step(
        context(),
        record_shadow_telemetry=True,
        shadow_telemetry_path=output_path,
    )

    assert len(calls) == 1
    comparison, timestamp, received_path = calls[0]
    assert comparison.run_id == "run-x"
    assert comparison.evaluated is True
    assert comparison.divergence_type is ShadowDivergenceType.AGREEMENT
    assert timestamp == STARTED_AT
    assert received_path == output_path
    assert_historical_payload(payload)


def test_opt_in_records_unavailable_comparison(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = isolate_monitor(monkeypatch)
    captured = []
    monkeypatch.setattr(
        pipeline,
        "append_shadow_comparison",
        lambda comparison, **_kwargs: captured.append(comparison),
    )

    pipeline._run_monitor_step(
        context(complete=False),
        record_shadow_telemetry=True,
        shadow_telemetry_path=tmp_path / "shadow.jsonl",
    )

    assert len(captured) == 1
    assert captured[0].evaluated is False
    assert captured[0].divergence_type is ShadowDivergenceType.UNAVAILABLE
    assert captured[0].missing_sources
    assert_historical_payload(payload, expected_privacy_risk=88)


def test_telemetry_failure_logs_warning_and_does_not_block_historical_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)

    def fail(*_args, **_kwargs):
        raise OSError("diagnostic storage unavailable")

    monkeypatch.setattr(pipeline, "append_shadow_comparison", fail)

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=tmp_path / "shadow.jsonl",
        )

    assert "Falha ao registrar telemetria shadow" in caplog.text
    assert "diagnostic storage unavailable" in caplog.text
    assert_historical_payload(payload)


def test_cli_flag_is_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "sys.argv", ["run_platform_pipeline", "--record-shadow-telemetry"]
    )

    args = pipeline.parse_args()

    assert args.record_shadow_telemetry is True
