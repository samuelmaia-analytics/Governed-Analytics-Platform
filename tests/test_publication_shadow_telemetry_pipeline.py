from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

import src.publication_shadow.telemetry as shadow_telemetry
import src.run_platform_pipeline as pipeline
from src.monitoring_components.models import MonitoringCheckResult
from src.observability_components.models import ObservabilityCheck
from src.publication_provenance import PipelineGovernanceContext
from src.publication_shadow import ShadowDivergenceType
from src.publication_shadow.execution_identity_manifest import (
    ExecutionIdentityManifest,
    IdentityStatus,
    ManifestEvidenceEntry,
)
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


def test_capture_flag_does_not_enable_shadow_writer(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = isolate_monitor(monkeypatch)
    monkeypatch.setattr(
        pipeline,
        "append_shadow_comparison",
        lambda *args, **kwargs: pytest.fail("shadow telemetry writer must not run"),
    )

    pipeline._run_monitor_step(context(), capture_shadow_manifest_entries=True)

    assert_historical_payload(payload)


def test_capture_default_off_does_not_invoke_factory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"

    created: list[object] = []
    original_collector = pipeline.InMemoryExecutionManifestCollector

    class SpyCollector(original_collector):
        def __init__(self, *, run_id: str | None, dataset_name: str | None = None) -> None:
            super().__init__(run_id=run_id, dataset_name=dataset_name)
            created.append(self)

    monkeypatch.setattr(pipeline, "InMemoryExecutionManifestCollector", SpyCollector)

    def fail(*_args, **_kwargs):
        raise RuntimeError("factory must not be called when capture is off")

    monkeypatch.setattr(shadow_telemetry, "build_manifest_evidence_entry", fail)

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=output_path,
        )

    assert created == []
    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert "Observational manifest capture failed" not in caplog.text
    assert_historical_payload(payload)


def test_capture_enabled_wires_collector_callback_and_preserves_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"

    created: list[object] = []
    original_collector = pipeline.InMemoryExecutionManifestCollector

    class SpyCollector(original_collector):
        def __init__(self, *, run_id: str | None, dataset_name: str | None = None) -> None:
            super().__init__(run_id=run_id, dataset_name=dataset_name)
            created.append(self)

    monkeypatch.setattr(pipeline, "InMemoryExecutionManifestCollector", SpyCollector)

    pipeline._run_monitor_step(
        context(),
        record_shadow_telemetry=True,
        shadow_telemetry_path=output_path,
        capture_shadow_manifest_entries=True,
    )

    assert len(created) == 1
    collector = created[0]

    assert collector.run_id == "run-x"
    assert collector.dataset_name is None

    contents = output_path.read_text(encoding="utf-8")
    assert contents.count("\n") == 1

    entries = collector.snapshot_entries()
    assert len(entries) == 1
    entry = entries[0]
    assert entry.evidence_type == shadow_telemetry.SHADOW_COMPARISON_EVIDENCE_TYPE
    assert entry.evidence_origin == shadow_telemetry.SHADOW_COMPARISON_EVIDENCE_ORIGIN
    assert entry.artifact_reference == str(output_path)
    assert entry.identity_status is IdentityStatus.MISSING

    manifest = collector.build_execution_identity_manifest_v1()
    assert manifest.run_id == "run-x"
    assert manifest.dataset_name is None
    assert manifest.authorizes_publication is False
    assert len(manifest.entries) == 1

    assert_historical_payload(payload)


def test_manifest_consumer_default_off_does_not_receive_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"
    received: list[ExecutionIdentityManifest] = []

    def consume(manifest: ExecutionIdentityManifest) -> None:
        received.append(manifest)

    pipeline._run_monitor_step(
        context(),
        record_shadow_telemetry=True,
        shadow_telemetry_path=output_path,
        consume_shadow_manifest_snapshot_fn=consume,
    )

    assert received == []
    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert_historical_payload(payload)


def test_manifest_consumer_receives_execution_identity_manifest_after_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"
    received: list[ExecutionIdentityManifest] = []

    def consume(manifest: ExecutionIdentityManifest) -> None:
        received.append(manifest)

    pipeline._run_monitor_step(
        context(),
        record_shadow_telemetry=True,
        shadow_telemetry_path=output_path,
        capture_shadow_manifest_entries=True,
        consume_shadow_manifest_snapshot_fn=consume,
    )

    assert len(received) == 1
    manifest = received[0]
    assert isinstance(manifest, ExecutionIdentityManifest)
    assert manifest.run_id == "run-x"
    assert manifest.dataset_name is None
    assert manifest.authorizes_publication is False
    assert len(manifest.entries) == 1

    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert_historical_payload(payload)


def test_manifest_consumer_snapshot_empty_does_not_deliver(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"
    received: list[ExecutionIdentityManifest] = []

    def append_stub(
        _comparison,
        *,
        timestamp_utc,
        output_path: Path,
        capture_manifest_entry_fn=None,
    ) -> Path:
        # Simula escrita bem-sucedida, mas não registra evidence no coletor.
        output_path.write_text("{}\n", encoding="utf-8")
        return output_path

    monkeypatch.setattr(pipeline, "append_shadow_comparison", append_stub)

    def consume(manifest: ExecutionIdentityManifest) -> None:
        received.append(manifest)

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=output_path,
            capture_shadow_manifest_entries=True,
            consume_shadow_manifest_snapshot_fn=consume,
        )

    assert received == []
    assert "Observational manifest snapshot consumption failed" not in caplog.text
    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert_historical_payload(payload)


def test_manifest_consumer_factory_failure_keeps_writer_behavior_and_skips_delivery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"
    received: list[ExecutionIdentityManifest] = []

    def fail(*_args, **_kwargs):
        raise OSError("factory unavailable")

    monkeypatch.setattr(shadow_telemetry, "build_manifest_evidence_entry", fail)

    def consume(manifest: ExecutionIdentityManifest) -> None:
        received.append(manifest)

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=output_path,
            capture_shadow_manifest_entries=True,
            consume_shadow_manifest_snapshot_fn=consume,
        )

    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert "Observational manifest capture failed" in caplog.text
    assert "factory unavailable" in caplog.text
    assert received == []
    assert "Observational manifest snapshot consumption failed" not in caplog.text
    assert_historical_payload(payload)


def test_manifest_consumer_writer_failure_does_not_deliver_and_preserves_warning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"
    received: list[ExecutionIdentityManifest] = []

    def fail(*_args, **_kwargs):
        raise OSError("diagnostic storage unavailable")

    monkeypatch.setattr(pipeline, "append_shadow_comparison", fail)

    def consume(manifest: ExecutionIdentityManifest) -> None:
        received.append(manifest)

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=output_path,
            capture_shadow_manifest_entries=True,
            consume_shadow_manifest_snapshot_fn=consume,
        )

    assert "Falha ao registrar telemetria shadow" in caplog.text
    assert "diagnostic storage unavailable" in caplog.text
    assert received == []
    assert "Observational manifest snapshot consumption failed" not in caplog.text
    assert_historical_payload(payload)


def test_manifest_consumer_isolated_between_invocations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    isolate_monitor(monkeypatch)
    received: list[ExecutionIdentityManifest] = []

    def consume(manifest: ExecutionIdentityManifest) -> None:
        received.append(manifest)

    ctx_a = PipelineGovernanceContext("run-a", started_at=STARTED_AT)
    ctx_b = PipelineGovernanceContext("run-b", started_at=STARTED_AT)
    out_a = tmp_path / "a.jsonl"
    out_b = tmp_path / "b.jsonl"

    pipeline._run_monitor_step(
        ctx_a,
        record_shadow_telemetry=True,
        shadow_telemetry_path=out_a,
        capture_shadow_manifest_entries=True,
        consume_shadow_manifest_snapshot_fn=consume,
    )
    pipeline._run_monitor_step(
        ctx_b,
        record_shadow_telemetry=True,
        shadow_telemetry_path=out_b,
        capture_shadow_manifest_entries=True,
        consume_shadow_manifest_snapshot_fn=consume,
    )

    assert len(received) == 2
    manifest_a, manifest_b = received
    assert manifest_a.run_id == "run-a"
    assert manifest_b.run_id == "run-b"
    assert manifest_a.entries[0].artifact_reference == str(out_a)
    assert manifest_b.entries[0].artifact_reference == str(out_b)
    assert out_a.read_text(encoding="utf-8").count("\n") == 1
    assert out_b.read_text(encoding="utf-8").count("\n") == 1

def test_manifest_consumer_failure_logs_warning_and_does_not_block_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"

    def consume(_manifest: ExecutionIdentityManifest) -> None:
        raise RuntimeError("consumer failed")

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=output_path,
            capture_shadow_manifest_entries=True,
            consume_shadow_manifest_snapshot_fn=consume,
        )

    assert "Observational manifest snapshot consumption failed" in caplog.text
    assert "consumer failed" in caplog.text
    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert_historical_payload(payload)


def test_manifest_consumer_manifest_build_failure_logs_warning_and_is_observational(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"

    created: list[object] = []
    original_collector = pipeline.InMemoryExecutionManifestCollector

    class SpyCollector(original_collector):
        def __init__(self, *, run_id: str | None, dataset_name: str | None = None) -> None:
            super().__init__(run_id=run_id, dataset_name=dataset_name)
            created.append(self)

        def build_execution_identity_manifest_v1(self) -> ExecutionIdentityManifest:
            raise RuntimeError("manifest build failed")

    monkeypatch.setattr(pipeline, "InMemoryExecutionManifestCollector", SpyCollector)

    def consume(_manifest: ExecutionIdentityManifest) -> None:
        pytest.fail("consumer should not receive manifest when build fails")

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=output_path,
            capture_shadow_manifest_entries=True,
            consume_shadow_manifest_snapshot_fn=consume,
        )

    assert len(created) == 1
    collector = created[0]
    assert collector.run_id == "run-x"
    assert collector.dataset_name is None

    assert "Observational manifest snapshot consumption failed" in caplog.text
    assert "manifest build failed" in caplog.text
    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert_historical_payload(payload)


def test_capture_factory_failure_logs_warning_and_does_not_block_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"

    created: list[object] = []
    original_collector = pipeline.InMemoryExecutionManifestCollector

    class SpyCollector(original_collector):
        def __init__(self, *, run_id: str | None, dataset_name: str | None = None) -> None:
            super().__init__(run_id=run_id, dataset_name=dataset_name)
            created.append(self)

    monkeypatch.setattr(pipeline, "InMemoryExecutionManifestCollector", SpyCollector)

    def fail(*_args, **_kwargs):
        raise OSError("factory unavailable")

    monkeypatch.setattr(shadow_telemetry, "build_manifest_evidence_entry", fail)

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=output_path,
            capture_shadow_manifest_entries=True,
        )

    assert len(created) == 1
    collector = created[0]

    assert "Observational manifest capture failed" in caplog.text
    assert "factory unavailable" in caplog.text
    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert collector.snapshot_entries() == ()
    assert_historical_payload(payload)


def test_capture_callback_failure_logs_warning_and_does_not_block_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)
    output_path = tmp_path / "shadow.jsonl"

    created: list[object] = []
    original_collector = pipeline.InMemoryExecutionManifestCollector

    class SpyCollector(original_collector):
        def __init__(self, *, run_id: str | None, dataset_name: str | None = None) -> None:
            super().__init__(run_id=run_id, dataset_name=dataset_name)
            created.append(self)

        def capture(self, entry) -> None:
            raise RuntimeError("callback failure")

    monkeypatch.setattr(pipeline, "InMemoryExecutionManifestCollector", SpyCollector)

    with caplog.at_level("WARNING"):
        pipeline._run_monitor_step(
            context(),
            record_shadow_telemetry=True,
            shadow_telemetry_path=output_path,
            capture_shadow_manifest_entries=True,
        )

    assert len(created) == 1
    collector = created[0]

    assert "Observational manifest capture failed" in caplog.text
    assert "callback failure" in caplog.text
    assert output_path.read_text(encoding="utf-8").count("\n") == 1
    assert collector.snapshot_entries() == ()
    assert_historical_payload(payload)


def test_capture_isolated_between_executions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    isolate_monitor(monkeypatch)

    created: list[object] = []
    original_collector = pipeline.InMemoryExecutionManifestCollector

    class SpyCollector(original_collector):
        def __init__(self, *, run_id: str | None, dataset_name: str | None = None) -> None:
            super().__init__(run_id=run_id, dataset_name=dataset_name)
            created.append(self)

    monkeypatch.setattr(pipeline, "InMemoryExecutionManifestCollector", SpyCollector)

    ctx_a = PipelineGovernanceContext("run-a", started_at=STARTED_AT)
    ctx_b = PipelineGovernanceContext("run-b", started_at=STARTED_AT)

    out_a = tmp_path / "a.jsonl"
    out_b = tmp_path / "b.jsonl"

    pipeline._run_monitor_step(
        ctx_a,
        record_shadow_telemetry=True,
        shadow_telemetry_path=out_a,
        capture_shadow_manifest_entries=True,
    )
    pipeline._run_monitor_step(
        ctx_b,
        record_shadow_telemetry=True,
        shadow_telemetry_path=out_b,
        capture_shadow_manifest_entries=True,
    )

    assert len(created) == 2
    collector_a, collector_b = created

    assert collector_a is not collector_b
    assert collector_a.run_id == "run-a"
    assert collector_b.run_id == "run-b"

    entries_a = collector_a.snapshot_entries()
    entries_b = collector_b.snapshot_entries()

    assert len(entries_a) == 1
    assert len(entries_b) == 1

    assert entries_a[0].artifact_reference == str(out_a)
    assert entries_b[0].artifact_reference == str(out_b)

    assert out_a.read_text(encoding="utf-8").count("\n") == 1
    assert out_b.read_text(encoding="utf-8").count("\n") == 1


def test_dispatch_capture_does_not_enable_shadow_writer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = isolate_monitor(monkeypatch)
    monkeypatch.setattr(
        pipeline,
        "append_shadow_comparison",
        lambda *args, **kwargs: pytest.fail("shadow telemetry writer must not run"),
    )

    with pipeline.activate_pipeline_governance_context(context()):
        pipeline.execute_step("monitor", capture_shadow_manifest_entries=True)

    assert_historical_payload(payload)


def test_dispatch_wires_capture_callback_via_execute_step(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = isolate_monitor(monkeypatch)

    created: list[object] = []
    original_collector = pipeline.InMemoryExecutionManifestCollector

    class SpyCollector(original_collector):
        def __init__(self, *, run_id: str | None, dataset_name: str | None = None) -> None:
            super().__init__(run_id=run_id, dataset_name=dataset_name)
            created.append(self)

    monkeypatch.setattr(pipeline, "InMemoryExecutionManifestCollector", SpyCollector)

    def append_stub(
        comparison,
        *,
        timestamp_utc,
        output_path,
        capture_manifest_entry_fn=None,
    ):
        assert capture_manifest_entry_fn is not None
        capture_manifest_entry_fn(
            ManifestEvidenceEntry(
                evidence_type=shadow_telemetry.SHADOW_COMPARISON_EVIDENCE_TYPE,
                evidence_origin=shadow_telemetry.SHADOW_COMPARISON_EVIDENCE_ORIGIN,
                artifact_reference=str(output_path),
                identity_status=IdentityStatus.MISSING,
            )
        )
        return output_path

    monkeypatch.setattr(pipeline, "append_shadow_comparison", append_stub)

    tok_shadow = pipeline._ACTIVE_SHADOW_ENABLED.set(True)
    try:
        with caplog.at_level("WARNING"):
            with pipeline.activate_pipeline_governance_context(context()):
                pipeline.execute_step("monitor", capture_shadow_manifest_entries=True)
    finally:
        pipeline._ACTIVE_SHADOW_ENABLED.reset(tok_shadow)

    assert len(created) == 1
    collector = created[0]
    assert collector.run_id == "run-x"
    assert collector.dataset_name is None

    entries = collector.snapshot_entries()
    assert len(entries) == 1
    assert entries[0].identity_status is IdentityStatus.MISSING

    assert "Falha ao registrar telemetria shadow" not in caplog.text
    assert_historical_payload(payload)



def test_run_selected_steps_does_not_pass_consumer_when_capture_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[tuple[str, object]] = []

    def execute_spy(step_name: str) -> None:
        called.append((step_name, None))

    monkeypatch.setattr(pipeline, "execute_step", execute_spy)

    def consumer(_manifest: ExecutionIdentityManifest) -> None:
        pass
    pipeline.run_selected_steps(["inventory"], consume_shadow_manifest_snapshot_fn=consumer)

    assert called == [("inventory", None)]


def test_run_selected_steps_passes_consumer_when_capture_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[tuple[str, bool, bool]] = []

    def consumer(_manifest: ExecutionIdentityManifest) -> None:
        pass

    def execute_spy(
        step_name: str,
        *,
        capture_shadow_manifest_entries: bool = False,
        consume_shadow_manifest_snapshot_fn=None,
    ) -> None:
        called.append(
            (
                step_name,
                capture_shadow_manifest_entries,
                consume_shadow_manifest_snapshot_fn is consumer,
            )
        )

    monkeypatch.setattr(pipeline, "execute_step", execute_spy)

    pipeline.run_selected_steps(
        ["inventory"],
        capture_shadow_manifest_entries=True,
        consume_shadow_manifest_snapshot_fn=consumer,
    )

    assert called == [("inventory", True, True)]


def test_run_selected_steps_accepts_positional_continue_on_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called_steps: list[str] = []

    monkeypatch.setitem(
        pipeline.STEP_HANDLERS, "build", lambda: called_steps.append("build")
    )

    def failing_publish() -> None:
        called_steps.append("publish")
        raise RuntimeError("publish failed")

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "publish", failing_publish)

    with pytest.raises(
        RuntimeError, match="Pipeline finalizado com falhas nas etapas: publish"
    ):
        pipeline.run_selected_steps(["build", "publish"], True)

    assert called_steps == ["build", "publish"]


def test_execute_step_monitor_consumer_default_off_does_not_pass_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[str] = []

    def monitor_handler() -> None:
        called.append("monitor")

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "monitor", monitor_handler)

    pipeline.execute_step(
        "monitor",
        consume_shadow_manifest_snapshot_fn=lambda _manifest: None,
    )

    assert called == ["monitor"]


def test_execute_step_monitor_handler_without_kwargs_is_compatible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[str] = []

    def monitor_handler() -> None:
        called.append("monitor")

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "monitor", monitor_handler)

    pipeline.execute_step("monitor")
    pipeline.execute_step("monitor", capture_shadow_manifest_entries=False)

    assert called == ["monitor", "monitor"]


def test_execute_step_monitor_capture_true_passes_kwarg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: list[bool] = []

    def monitor_handler(*, capture_shadow_manifest_entries: bool = False) -> None:
        received.append(capture_shadow_manifest_entries)

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "monitor", monitor_handler)

    pipeline.execute_step("monitor", capture_shadow_manifest_entries=True)

    assert received == [True]


def test_execute_step_other_steps_remain_zero_arg(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[str] = []
    monkeypatch.setitem(pipeline.STEP_HANDLERS, "inventory", lambda: called.append("inventory"))

    pipeline.execute_step("inventory")

    assert called == ["inventory"]
