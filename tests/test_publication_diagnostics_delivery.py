from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import src.run_platform_pipeline as pipeline
from app.pages.publication_governance import load_publication_governance_snapshot
from src.monitoring_components.models import MonitoringCheckResult
from src.observability_components.models import ObservabilityCheck
from src.publish_components.models import PrivacyCheck
from src.quality_components.models import QualityCheckResult
from src.schema_contract_components.models import ContractCheck


def test_cli_produces_same_run_evidence_readable_by_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Real JSONL writers and page reader, with synthetic pipeline inputs."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_platform_pipeline",
            "--steps",
            "contracts",
            "quality",
            "publish",
            "monitor",
            "--record-shadow-telemetry",
            "--record-dual-privacy-telemetry",
            "--record-content-provenance",
        ],
    )
    monkeypatch.setattr(pipeline, "configure_logging", lambda: None)
    monkeypatch.setattr(pipeline, "PATHS", SimpleNamespace(validate=lambda: None))
    monkeypatch.setattr(pipeline, "save_pipeline_execution_report", lambda *_a: None)
    monkeypatch.setattr(
        pipeline, "load_fact_table", lambda: pd.DataFrame({"price": [10.0]})
    )
    monkeypatch.setattr(
        pipeline,
        "run_quality_checks",
        lambda _df: [QualityCheckResult("quality", "PASS", 0, 0, "high", "ok")],
    )
    monkeypatch.setattr(pipeline, "save_quality_results", lambda *_a: None)
    monkeypatch.setattr(pipeline, "save_quality_report", lambda *_a: None)
    monkeypatch.setattr(
        pipeline,
        "schema_contracts_main",
        lambda *, capture_results_fn: capture_results_fn(
            [ContractCheck("fact_orders_enriched", "gold", "schema", "PASS", "ok")]
        ),
    )
    source = pd.DataFrame(
        {
            "order_id": ["synthetic-order"],
            "order_item_id": [1],
            "product_id": ["synthetic-product"],
            "seller_id": ["synthetic-seller"],
            "email": ["synthetic@example.invalid"],
            "price": [10.0],
        }
    )
    published = source[["order_id", "order_item_id", "price"]].copy()
    monkeypatch.setattr(
        pipeline,
        "run_publish_dashboard",
        lambda *, capture_privacy_material_fn: capture_privacy_material_fn(
            source,
            published,
            [
                PrivacyCheck("forbidden_columns_absent", "PASS", "ok"),
                PrivacyCheck("classification_leakage", "PASS", "ok"),
                PrivacyCheck("pseudonymized__order_id", "PASS", "synthetic token"),
            ],
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "run_monitoring",
        lambda: [
            MonitoringCheckResult(
                "published_file_freshness_hours", "PASS", 1, 36, "high", "ok"
            )
        ],
    )
    monkeypatch.setattr(pipeline, "save_published_monitoring_results", lambda *_a: None)
    monkeypatch.setattr(pipeline, "save_published_monitoring_report", lambda *_a: None)
    monkeypatch.setattr(pipeline, "load_published_monitoring_frame", lambda: published)
    monkeypatch.setattr(
        pipeline,
        "load_governance_history",
        lambda: pd.DataFrame({"data_quality_score": [73], "privacy_risk_score": [88]}),
    )
    monkeypatch.setattr(
        pipeline,
        "evaluate_governance_observability",
        lambda **_kw: [ObservabilityCheck("freshness", "PASS", "low", 0, 0, "ok")],
    )
    monkeypatch.setattr(pipeline, "save_observability_results", lambda *_a: None)
    historical: dict[str, object] = {}
    monkeypatch.setattr(
        pipeline,
        "save_publication_decision_artifact",
        lambda **kwargs: historical.update(kwargs),
    )
    paths = {
        "append_shadow_comparison": tmp_path / "publication_shadow_comparisons.jsonl",
        "append_dual_privacy_comparison": tmp_path
        / "dual_privacy_shadow_comparisons.jsonl",
        "append_dataset_content_provenance": tmp_path
        / "dataset_content_provenance.jsonl",
    }

    def redirect(writer, destination):
        def append(record, *, timestamp_utc, output_path):
            assert output_path.name == destination.name
            return writer(record, timestamp_utc=timestamp_utc, output_path=destination)

        return append

    for name, destination in paths.items():
        monkeypatch.setattr(
            pipeline, name, redirect(getattr(pipeline, name), destination)
        )

    pipeline.main()

    records = [json.loads(path.read_text(encoding="utf-8")) for path in paths.values()]
    assert len({record["run_id"] for record in records}) == 1
    assert records[0]["evaluated"] is True
    assert records[1]["evaluated"] is True
    assert "synthetic@example.invalid" not in "".join(
        path.read_text() for path in paths.values()
    )
    decision_path = tmp_path / "decision.json"
    decision_path.write_text(json.dumps({"status": historical["publication_status"]}))
    missing = tmp_path / "absent.csv"
    snapshot = load_publication_governance_snapshot(
        decision_path=decision_path,
        shadow_path=paths["append_shadow_comparison"],
        dual_path=paths["append_dual_privacy_comparison"],
        content_path=paths["append_dataset_content_provenance"],
        privacy_path=missing,
        schema_path=missing,
        business_path=missing,
        quality_path=missing,
        monitoring_path=missing,
    )
    assert snapshot.execution_provenance == "Valid · same run"
    assert snapshot.content_provenance == "Recorded · same run"
    assert snapshot.shadow_decision != "Unavailable"
    assert snapshot.residual_decision != "Unavailable"
    assert historical["privacy_risk_score"] == 88
    assert historical["data_quality_score"] == 73
    assert historical["publication_status"] == "Approved"
    assert pipeline._ACTIVE_GOVERNANCE_CONTEXT.get() is None
    assert not pipeline._ACTIVE_SHADOW_ENABLED.get()
    assert not pipeline._ACTIVE_DUAL_ENABLED.get()
    assert not pipeline._ACTIVE_CONTENT_PROVENANCE_ENABLED.get()


def test_diagnostic_flags_reset_when_metadata_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.argv", ["pipeline", "--record-shadow-telemetry"])
    monkeypatch.setattr(pipeline, "configure_logging", lambda: None)
    monkeypatch.setattr(pipeline, "PATHS", SimpleNamespace(validate=lambda: None))
    monkeypatch.setattr(pipeline, "run_selected_steps", lambda *_a, **_kw: [])

    def fail(*_a):
        raise RuntimeError("metadata unavailable")

    monkeypatch.setattr(pipeline, "build_run_metadata", fail)
    with pytest.raises(RuntimeError, match="metadata unavailable"):
        pipeline.main()
    assert pipeline._ACTIVE_GOVERNANCE_CONTEXT.get() is None
    assert not pipeline._ACTIVE_SHADOW_ENABLED.get()
