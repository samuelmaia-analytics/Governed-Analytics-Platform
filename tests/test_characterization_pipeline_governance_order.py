from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

import scripts.run_governance_pipeline as runner
import src.business_rule_validation as business_rules
import src.governance_scorecards as scorecards
import src.publish_dashboard as publication
import src.published_monitoring as monitoring
import src.quality as quality
import src.run_platform_pipeline as pipeline
import src.schema_contracts as contracts
from src.business_rule_validation import BusinessRuleResult
from src.governance_history import save_publication_decision_artifact
from src.publication_provenance import PipelineGovernanceContext
from src.publish_components.models import PrivacyCheck, PrivacyPreflightResult
from src.published_monitoring import MonitoringCheckResult
from src.quality import QualityCheckResult
from src.schema_contracts import ContractCheck
from src.scorecard_components.models import ScorecardMetric

EXPECTED_ORDER = [
    "inventory",
    "profiling",
    "build",
    "classify",
    "contracts",
    "business_rules",
    "quality",
    "publish",
    "semantic",
    "monitor",
    "scorecards",
    "lineage",
    "catalog",
    "queries",
    "screenshots",
    "bi",
]


def test_pipeline_governance_order_is_frozen() -> None:
    order = [step.name for step in pipeline.PIPELINE_STEPS]

    assert order == EXPECTED_ORDER
    assert order.index("contracts") < order.index("quality") < order.index("publish")
    assert order.index("business_rules") < order.index("publish")
    assert order.index("quality") < order.index("publish")
    assert order.index("monitor") > order.index("contracts")
    assert order.index("monitor") > order.index("business_rules")
    assert order.index("monitor") > order.index("quality")
    assert order.index("scorecards") > order.index("monitor")


@pytest.mark.parametrize(
    ("monitor_statuses", "expected_decision"),
    [(["PASS", "PASS"], "Approved"), (["PASS", "FAIL"], "Needs Review")],
)
def test_monitor_step_uses_only_monitoring_failures_for_decision(
    monitor_statuses: list[str], expected_decision: str, monkeypatch
) -> None:
    calls: list[str] = []
    results = [
        MonitoringCheckResult(
            "published_file_freshness_hours",
            monitor_statuses[0],
            0,
            36,
            "high",
            "freshness",
        ),
        MonitoringCheckResult(
            "another_check", monitor_statuses[1], 0, 0, "high", "detail"
        ),
    ]
    history = pd.DataFrame({"data_quality_score": [73], "privacy_risk_score": [88]})
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        pipeline, "run_monitoring", lambda: calls.append("monitor") or results
    )
    monkeypatch.setattr(
        pipeline,
        "save_published_monitoring_results",
        lambda value: calls.append("save_results"),
    )
    monkeypatch.setattr(
        pipeline,
        "save_published_monitoring_report",
        lambda value: calls.append("save_report"),
    )
    monkeypatch.setattr(
        pipeline,
        "load_published_monitoring_frame",
        lambda: calls.append("load_published") or pd.DataFrame({"a": [1]}),
    )
    monkeypatch.setattr(
        pipeline,
        "load_governance_history",
        lambda: calls.append("load_history") or history,
    )
    monkeypatch.setattr(
        pipeline,
        "evaluate_governance_observability",
        lambda **kwargs: calls.append("observability") or ["check"],
    )
    monkeypatch.setattr(
        pipeline,
        "save_observability_results",
        lambda checks: calls.append("save_observability"),
    )

    def save_decision(**kwargs: object) -> None:
        calls.append("decision")
        captured.update(kwargs)

    monkeypatch.setattr(pipeline, "save_publication_decision_artifact", save_decision)
    monkeypatch.setattr(pipeline, "EXPECTED_COLUMNS", {"a"})

    pipeline._run_monitor_step()

    assert calls == [
        "monitor",
        "save_results",
        "save_report",
        "load_published",
        "load_history",
        "observability",
        "save_observability",
        "decision",
    ]
    assert captured["publication_status"] == expected_decision
    assert captured["failed_checks_count"] == monitor_statuses.count("FAIL")
    assert captured["data_quality_score"] == 73
    assert captured["privacy_risk_score"] == 88
    assert expected_decision != "Blocked"


@pytest.fixture
def governance_snapshots(tmp_path: Path, monkeypatch):
    quality_dir = tmp_path / "quality"
    monitoring_dir = tmp_path / "monitoring"
    for module in (quality, contracts, business_rules, publication):
        monkeypatch.setattr(module, "QUALITY_DIR", quality_dir)
    quality_path = quality_dir / "quality.csv"
    schema_path = quality_dir / "schema.csv"
    business_path = quality_dir / "business.csv"
    privacy_path = quality_dir / "privacy.csv"
    monitor_path = monitoring_dir / "monitor.csv"
    scorecard_path = monitoring_dir / "scorecards.csv"
    monkeypatch.setattr(quality, "QUALITY_RESULTS_PATH", quality_path)
    monkeypatch.setattr(contracts, "RESULTS_PATH", schema_path)
    monkeypatch.setattr(business_rules, "RESULTS_PATH", business_path)
    monkeypatch.setattr(publication, "PRIVACY_RESULTS_PATH", privacy_path)
    monkeypatch.setattr(monitoring, "PUBLISHED_MONITORING_DIR", monitoring_dir)
    monkeypatch.setattr(monitoring, "RESULTS_PATH", monitor_path)
    monkeypatch.setattr(monitoring, "SUMMARY_PATH", monitoring_dir / "monitor.json")
    monkeypatch.setattr(scorecards, "PUBLISHED_MONITORING_DIR", monitoring_dir)
    monkeypatch.setattr(scorecards, "SCORECARD_CSV_PATH", scorecard_path)
    monkeypatch.setattr(
        scorecards, "SCORECARD_JSON_PATH", monitoring_dir / "scorecards.json"
    )

    quality.save_quality_results(
        [QualityCheckResult("quality", "PASS", 0, 0, "high", "ok")]
    )
    contracts.save_results([ContractCheck("demo", "curated", "schema", "PASS", "ok")])
    business_rules.save_results(
        [BusinessRuleResult("rule", "PASS", "high", 0, 0.0, "ok")]
    )
    publication.save_privacy_results([PrivacyCheck("privacy", "PASS", "ok")])
    monitoring.save_results(
        [MonitoringCheckResult("freshness", "PASS", 0, 36, "high", "ok")]
    )
    scorecards.save_outputs(
        [ScorecardMetric("demo", "quality", 100, "healthy", "quality.csv", 1, 0)], []
    )
    decision_path = save_publication_decision_artifact(
        dataset_name="demo",
        publication_status="Approved",
        data_quality_score=100,
        privacy_risk_score=20,
        failed_checks_count=0,
        timestamp_utc="2026-01-01T00:00:00+00:00",
        output_path=monitoring_dir / "decision.json",
    )
    return [
        quality_path,
        schema_path,
        business_path,
        privacy_path,
        monitor_path,
        scorecard_path,
    ], decision_path


def test_governance_csv_snapshots_and_decision_have_no_run_id(
    governance_snapshots,
) -> None:
    paths, decision_path = governance_snapshots
    assert all(path.exists() for path in paths)
    assert all("run_id" not in pd.read_csv(path).columns for path in paths)
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert list(decision) == [
        "dataset",
        "status",
        "quality_score",
        "privacy_risk_score",
        "failed_checks",
        "timestamp_utc",
        "decision_reason",
    ]
    assert {
        "run_id",
        "canonical_decision",
        "divergence",
        "policy_id",
        "policy_version",
        "provenance",
    }.isdisjoint(decision)
    assert isinstance(decision["dataset"], str) and decision["dataset"]
    assert decision["status"] in {"Approved", "Needs Review", "Blocked"}
    assert isinstance(decision["quality_score"], (int, float))
    assert not isinstance(decision["quality_score"], bool)
    assert isinstance(decision["privacy_risk_score"], (int, float))
    assert not isinstance(decision["privacy_risk_score"], bool)
    assert isinstance(decision["failed_checks"], int)
    assert not isinstance(decision["failed_checks"], bool)
    assert decision["failed_checks"] >= 0
    timestamp = datetime.fromisoformat(decision["timestamp_utc"])
    assert timestamp.tzinfo is not None
    assert timestamp.utcoffset() is not None
    assert isinstance(decision["decision_reason"], str)
    assert decision["decision_reason"]


@pytest.mark.parametrize(
    ("quality_status", "privacy_status", "expected_decision"),
    [
        ("PASS", "PASS", "APPROVED"),
        ("FAIL", "PASS", "BLOCKED"),
        ("PASS", "FAIL", "BLOCKED"),
    ],
)
def test_publication_gate_preflights_before_publishing_and_blocks_failed_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    quality_status: str,
    privacy_status: str,
    expected_decision: str,
) -> None:
    events: list[str] = []
    artifact = tmp_path / "published.csv"
    context = PipelineGovernanceContext("run-characterization")
    quality_results = [
        QualityCheckResult("volume", quality_status, 1, 1, "high", "synthetic")
    ]
    source = pd.DataFrame({"order_id": ["synthetic-order"]})
    candidate = pd.DataFrame({"order_id": ["order_id_synthetic"]})

    def run_steps(steps, *, continue_on_error):
        assert continue_on_error is False
        events.extend(steps)
        if "quality" in steps:
            context.record_quality(quality_results)
        if "publish" in steps:
            assert "preflight" in events
            assert "decision" in events
            artifact.write_text("synthetic", encoding="utf-8")
        return []

    def preflight():
        events.append("preflight")
        assert not artifact.exists()
        return PrivacyPreflightResult(
            source,
            candidate,
            {},
            {},
            [PrivacyCheck("privacy", privacy_status, "synthetic")],
        )

    def save_decision(**payload):
        events.append("decision")
        assert events.index("preflight") < events.index("decision")
        assert not artifact.exists()
        assert payload["decision"] == expected_decision

    monkeypatch.setattr(runner, "run_selected_steps", run_steps)
    monkeypatch.setattr(runner, "run_privacy_preflight", preflight)
    monkeypatch.setattr(runner, "persist_quality_results_to_postgres", lambda *_: 1)
    monkeypatch.setattr(runner, "save_publication_decision", save_decision)

    outcome = runner.execute_governed_steps(
        selected_steps=["contracts", "quality", "publish"],
        continue_on_error=False,
        postgres_run_id=42,
        governance_context=context,
    )

    assert outcome.publication_gate is not None
    assert outcome.publication_gate.decision == expected_decision
    assert events[:4] == ["contracts", "quality", "preflight", "decision"]
    if expected_decision == "BLOCKED":
        assert events == ["contracts", "quality", "preflight", "decision"]
        assert not artifact.exists()
    else:
        assert events == ["contracts", "quality", "preflight", "decision", "publish"]
        assert artifact.read_text(encoding="utf-8") == "synthetic"
