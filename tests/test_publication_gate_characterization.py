from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from scripts.run_publication_gate import evaluate_publication_gate
from src.publication_gate import (
    evaluate_operational_publication_gate,
    evaluate_publication_readiness,
)


def test_yaml_contract_privacy_threshold_can_diverge_from_readiness_and_cli() -> None:
    contract_path = Path("contracts/published/fact_orders_dashboard.contract.yml")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    assert isinstance(contract, dict)

    policy = contract.get("publication_policy")
    assert isinstance(policy, dict)
    max_privacy = policy.get("maximum_privacy_risk_score")
    assert max_privacy == 70

    readiness = evaluate_publication_readiness(
        data_quality_score=90,
        privacy_risk_score=60,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert readiness.decision == "Needs Review"

    decision, _reason = evaluate_publication_gate(
        quality_score=90,
        lgpd_risk_score=60,
        critical_issues=0,
    )
    assert decision == "Approved"


def test_operational_gate_can_approve_while_readiness_requires_review() -> None:
    operational = evaluate_operational_publication_gate(
        total_checks=10,
        pass_checks=10,
        warn_checks=0,
        fail_checks=0,
        critical_failures=0,
        privacy_failed_checks=0,
    )
    assert operational.decision == "APPROVED"

    readiness = evaluate_publication_readiness(
        data_quality_score=79,
        privacy_risk_score=0,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert readiness.decision == "Needs Review"


def test_run_monitor_step_persists_publication_status_from_failed_checks_count(monkeypatch) -> None:
    import src.run_platform_pipeline as pipeline

    @dataclass(frozen=True)
    class DummyMonitoringResult:
        check_name: str
        status: str

    calls: list[dict[str, object]] = []

    def capture_decision(**kwargs):  # type: ignore[no-untyped-def]
        calls.append(kwargs)

    token = pipeline._ACTIVE_GOVERNANCE_CONTEXT.set(None)
    try:
        monkeypatch.setattr(pipeline, "save_publication_decision_artifact", capture_decision)
        monkeypatch.setattr(pipeline, "save_published_monitoring_results", lambda _r: None)
        monkeypatch.setattr(pipeline, "save_published_monitoring_report", lambda _r: None)
        monkeypatch.setattr(pipeline, "save_observability_results", lambda _r: None)
        monkeypatch.setattr(pipeline, "load_published_monitoring_frame", lambda: pd.DataFrame())
        monkeypatch.setattr(pipeline, "load_governance_history", lambda: pd.DataFrame())
        monkeypatch.setattr(
            pipeline,
            "evaluate_governance_observability",
            lambda **_kwargs: [],
        )

        monkeypatch.setattr(
            pipeline,
            "run_monitoring",
            lambda: [
                DummyMonitoringResult("published_file_freshness_hours", "PASS"),
                DummyMonitoringResult("any", "PASS"),
            ],
        )
        pipeline._run_monitor_step()

        assert calls[-1]["publication_status"] == "Approved"
        assert calls[-1]["failed_checks_count"] == 0
        assert calls[-1]["data_quality_score"] == 100

        monkeypatch.setattr(
            pipeline,
            "run_monitoring",
            lambda: [
                DummyMonitoringResult("published_file_freshness_hours", "PASS"),
                DummyMonitoringResult("any", "FAIL"),
            ],
        )
        pipeline._run_monitor_step()

        assert calls[-1]["publication_status"] == "Needs Review"
        assert calls[-1]["failed_checks_count"] == 1
        assert calls[-1]["data_quality_score"] == 90
    finally:
        pipeline._ACTIVE_GOVERNANCE_CONTEXT.reset(token)
