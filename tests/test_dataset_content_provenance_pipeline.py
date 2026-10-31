from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

import src.run_platform_pipeline as pipeline
from src.monitoring_components.models import MonitoringCheckResult
from src.observability_components.models import ObservabilityCheck
from src.publication_provenance import (
    PUBLISHED_CONTENT_KEY,
    SOURCE_CONTENT_KEY,
    PipelineGovernanceContext,
    fingerprint_dataframe_content,
)
from src.publish_components.models import PrivacyCheck

STARTED_AT = datetime(2026, 8, 15, 3, 30, tzinfo=UTC)


def _source() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o2"],
            "order_item_id": [1, 1],
            "product_id": ["p1", "p2"],
            "seller_id": ["s1", "s2"],
            "price": [10.0, 20.0],
        }
    )


def _published() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["order-a", "order-b"],
            "order_item_id": [1, 1],
            "seller_key": ["seller-a", "seller-b"],
            "price": [10.0, 20.0],
        }
    )


def _checks() -> list[PrivacyCheck]:
    return [
        PrivacyCheck("forbidden_columns_absent", "PASS", "ok"),
        PrivacyCheck("classification_leakage", "PASS", "ok"),
    ]


def _context() -> PipelineGovernanceContext:
    return PipelineGovernanceContext("run-current", started_at=STARTED_AT)


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


def test_default_skips_fingerprint_calculation_and_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "content.jsonl"
    monkeypatch.setattr(
        pipeline,
        "build_dataset_content_provenance",
        lambda **_kwargs: pytest.fail("fingerprint calculated by default"),
    )
    monkeypatch.setattr(
        pipeline,
        "append_dataset_content_provenance",
        lambda *args, **kwargs: pytest.fail("content writer called by default"),
    )

    pipeline._capture_publish_material(
        _context(),
        _source(),
        _published(),
        _checks(),
        content_provenance_path=output_path,
    )

    assert not output_path.exists()


def test_opt_in_writes_once_with_current_run_id_and_timestamp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, datetime, Path]] = []
    output_path = tmp_path / "content.jsonl"

    def append(provenance, *, timestamp_utc, output_path):
        calls.append((provenance, timestamp_utc, output_path))

    monkeypatch.setattr(pipeline, "append_dataset_content_provenance", append)

    pipeline._capture_publish_material(
        _context(),
        _source(),
        _published(),
        _checks(),
        record_content_provenance=True,
        content_provenance_path=output_path,
    )

    assert len(calls) == 1
    provenance, timestamp, received_path = calls[0]
    assert provenance.run_id == "run-current"
    assert timestamp == STARTED_AT
    assert received_path == output_path


def test_opt_in_fingerprints_current_source_and_published_objects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _source()
    published = _published()
    captured = []
    monkeypatch.setattr(
        pipeline,
        "append_dataset_content_provenance",
        lambda provenance, **_kwargs: captured.append(provenance),
    )

    pipeline._capture_publish_material(
        _context(),
        source,
        published,
        _checks(),
        record_content_provenance=True,
        content_provenance_path=tmp_path / "content.jsonl",
    )

    assert captured[0].source_content_fingerprint == fingerprint_dataframe_content(
        source, stable_key=SOURCE_CONTENT_KEY
    )
    assert captured[0].published_content_fingerprint == fingerprint_dataframe_content(
        published, stable_key=PUBLISHED_CONTENT_KEY
    )


def test_writer_failure_warns_and_historical_decision_continues(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    context = _context()
    historical_payload = _isolate_monitor(monkeypatch)

    def fail(*_args, **_kwargs):
        raise OSError("content diagnostic storage unavailable")

    monkeypatch.setattr(pipeline, "append_dataset_content_provenance", fail)

    with caplog.at_level("WARNING"):
        pipeline._capture_publish_material(
            context,
            _source(),
            _published(),
            _checks(),
            record_content_provenance=True,
            content_provenance_path=tmp_path / "content.jsonl",
        )
        pipeline._run_monitor_step(context)

    assert "Falha ao registrar dataset content provenance" in caplog.text
    assert "content diagnostic storage unavailable" in caplog.text
    assert historical_payload["publication_status"] == "Approved"


def test_content_writer_does_not_touch_shadow_or_dual_jsonl(tmp_path: Path) -> None:
    shadow_path = tmp_path / "publication_shadow_comparisons.jsonl"
    dual_path = tmp_path / "dual_privacy_shadow_comparisons.jsonl"
    shadow_bytes = b'{"existing":"shadow"}\n'
    dual_bytes = b'{"existing":"dual"}\n'
    shadow_path.write_bytes(shadow_bytes)
    dual_path.write_bytes(dual_bytes)

    pipeline._capture_publish_material(
        _context(),
        _source(),
        _published(),
        _checks(),
        record_content_provenance=True,
        content_provenance_path=tmp_path / "dataset_content_provenance.jsonl",
    )

    assert shadow_path.read_bytes() == shadow_bytes
    assert dual_path.read_bytes() == dual_bytes


def test_cli_flag_is_independent_explicit_opt_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["run_platform_pipeline", "--record-content-provenance"],
    )

    args = pipeline.parse_args()

    assert args.record_content_provenance is True
    assert args.record_shadow_telemetry is False
    assert args.record_dual_privacy_telemetry is False


def test_publish_step_forwards_active_content_opt_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: list[bool] = []
    context_token = pipeline._ACTIVE_GOVERNANCE_CONTEXT.set(_context())
    flag_token = pipeline._ACTIVE_CONTENT_PROVENANCE_ENABLED.set(True)

    def capture(
        _context,
        _source,
        _published,
        _results,
        *,
        record_content_provenance,
    ) -> None:
        received.append(record_content_provenance)

    def run_publish_dashboard(*, capture_privacy_material_fn) -> None:
        capture_privacy_material_fn(_source(), _published(), _checks())

    monkeypatch.setattr(pipeline, "_capture_publish_material", capture)
    monkeypatch.setattr(pipeline, "run_publish_dashboard", run_publish_dashboard)
    try:
        pipeline.execute_step("publish")
    finally:
        pipeline._ACTIVE_CONTENT_PROVENANCE_ENABLED.reset(flag_token)
        pipeline._ACTIVE_GOVERNANCE_CONTEXT.reset(context_token)

    assert received == [True]
