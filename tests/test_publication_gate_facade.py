from __future__ import annotations

import builtins
from dataclasses import FrozenInstanceError, asdict, fields
from pathlib import Path
from typing import get_args

import pytest

import src.publication_gate as domain_gate
import src.run_platform_pipeline as platform_pipeline
from scripts.run_publication_gate import evaluate_publication_gate

BASE_INPUTS: dict[str, object] = {
    "data_quality_score": 100,
    "privacy_risk_score": 0,
    "critical_rule_failures": 0,
    "freshness_status": "fresh",
    "schema_contract_status": "passed",
    "has_sensitive_data_without_protection": False,
}


def _evaluate(**overrides: object) -> domain_gate.PublicationReadinessDecision:
    inputs = BASE_INPUTS | overrides
    return domain_gate.evaluate_publication_readiness(**inputs)  # type: ignore[arg-type]


def test_public_api_types_constants_and_thresholds_are_stable() -> None:
    assert get_args(domain_gate.PublicationDecision) == (
        "Approved",
        "Needs Review",
        "Blocked",
    )
    assert get_args(domain_gate.PublicationSeverity) == (
        "Low",
        "Medium",
        "High",
        "Critical",
    )
    assert get_args(domain_gate.FreshnessStatus) == ("fresh", "warning", "stale")
    assert get_args(domain_gate.SchemaContractStatus) == ("passed", "failed")
    assert domain_gate.MIN_DATA_QUALITY_SCORE_REVIEW == 80
    assert domain_gate.PRIVACY_RISK_SCORE_REVIEW == 60
    assert domain_gate.PRIVACY_RISK_SCORE_HIGH == 80
    assert callable(domain_gate.evaluate_publication_readiness)


def test_decision_model_fields_serialization_equality_and_frozen_behavior() -> None:
    decision = domain_gate.PublicationReadinessDecision(
        decision="Approved",
        severity="Low",
        reasons=["reason"],
        required_actions=["action"],
    )
    equal = domain_gate.PublicationReadinessDecision(
        decision="Approved",
        severity="Low",
        reasons=["reason"],
        required_actions=["action"],
    )

    assert [field.name for field in fields(decision)] == [
        "decision",
        "severity",
        "reasons",
        "required_actions",
    ]
    assert decision == equal
    assert asdict(decision) == {
        "decision": "Approved",
        "severity": "Low",
        "reasons": ["reason"],
        "required_actions": ["action"],
    }
    with pytest.raises(FrozenInstanceError):
        decision.severity = "High"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("overrides", "decision", "severity"),
    [
        ({"data_quality_score": 79}, "Needs Review", "Medium"),
        ({"data_quality_score": 80}, "Approved", "Low"),
        ({"privacy_risk_score": 59}, "Approved", "Low"),
        ({"privacy_risk_score": 60}, "Needs Review", "Medium"),
        ({"privacy_risk_score": 79}, "Needs Review", "Medium"),
        ({"privacy_risk_score": 80}, "Needs Review", "High"),
        ({"critical_rule_failures": 0}, "Approved", "Low"),
        ({"critical_rule_failures": 1}, "Blocked", "Critical"),
        ({"schema_contract_status": "passed"}, "Approved", "Low"),
        ({"schema_contract_status": "failed"}, "Blocked", "Critical"),
        ({"has_sensitive_data_without_protection": False}, "Approved", "Low"),
        ({"has_sensitive_data_without_protection": True}, "Blocked", "Critical"),
        ({"freshness_status": "warning"}, "Needs Review", "Medium"),
        ({"freshness_status": "stale"}, "Needs Review", "High"),
    ],
)
def test_domain_threshold_boundaries_status_and_severity(
    overrides: dict[str, object], decision: str, severity: str
) -> None:
    result = _evaluate(**overrides)
    assert (result.decision, result.severity) == (decision, severity)


@pytest.mark.parametrize(
    ("overrides", "reason", "action"),
    [
        (
            {"critical_rule_failures": 1},
            "Critical rule failures detected: 1.",
            "Resolve critical quality rule failures before publication.",
        ),
        (
            {"has_sensitive_data_without_protection": True},
            "Sensitive data found without masking/anonymization.",
            "Mask, anonymize, or remove sensitive data before publication.",
        ),
        (
            {"schema_contract_status": "failed"},
            "Schema contract validation failed.",
            "Fix schema contract violations and revalidate.",
        ),
        (
            {"data_quality_score": 79},
            "Data quality score below recommended threshold (79 < 80).",
            "Investigate failed checks and improve data quality score.",
        ),
        (
            {"privacy_risk_score": 60},
            "Privacy risk score is elevated (60 >= 60).",
            "Review privacy controls and mitigation actions.",
        ),
        (
            {"freshness_status": "warning"},
            "Freshness status requires attention: warning.",
            "Refresh dataset and confirm SLA/freshness compliance.",
        ),
    ],
)
def test_each_condition_preserves_exact_reason_and_required_action(
    overrides: dict[str, object], reason: str, action: str
) -> None:
    result = _evaluate(**overrides)
    assert result.reasons == [reason]
    assert result.required_actions == [action]


def test_approved_reason_and_action_are_exact() -> None:
    result = _evaluate()

    assert result == domain_gate.PublicationReadinessDecision(
        decision="Approved",
        severity="Low",
        reasons=["All publication controls are within acceptable thresholds."],
        required_actions=["Proceed with publication and keep routine monitoring."],
    )


def test_all_bad_conditions_preserve_precedence_reason_and_action_order() -> None:
    result = _evaluate(
        data_quality_score=79,
        privacy_risk_score=80,
        critical_rule_failures=2,
        freshness_status="stale",
        schema_contract_status="failed",
        has_sensitive_data_without_protection=True,
    )

    assert (result.decision, result.severity) == ("Blocked", "Critical")
    assert result.reasons == [
        "Critical rule failures detected: 2.",
        "Sensitive data found without masking/anonymization.",
        "Schema contract validation failed.",
        "Data quality score below recommended threshold (79 < 80).",
        "Privacy risk score is elevated (80 >= 60).",
        "Freshness status requires attention: stale.",
    ]
    assert result.required_actions == [
        "Resolve critical quality rule failures before publication.",
        "Mask, anonymize, or remove sensitive data before publication.",
        "Fix schema contract violations and revalidate.",
        "Investigate failed checks and improve data quality score.",
        "Review privacy controls and mitigation actions.",
        "Refresh dataset and confirm SLA/freshness compliance.",
    ]


@pytest.mark.parametrize(
    ("overrides", "expected_severity"),
    [
        ({"data_quality_score": 79, "privacy_risk_score": 80}, "High"),
        ({"data_quality_score": 79, "schema_contract_status": "failed"}, "Critical"),
        ({"privacy_risk_score": 80, "critical_rule_failures": 1}, "Critical"),
        (
            {
                "schema_contract_status": "failed",
                "has_sensitive_data_without_protection": True,
            },
            "Critical",
        ),
    ],
)
def test_combined_rules_preserve_maximum_severity_and_blocking_precedence(
    overrides: dict[str, object], expected_severity: str
) -> None:
    result = _evaluate(**overrides)
    expected_decision = (
        "Blocked"
        if any(
            (
                overrides.get("critical_rule_failures", 0),
                overrides.get("schema_contract_status") == "failed",
                overrides.get("has_sensitive_data_without_protection", False),
            )
        )
        else "Needs Review"
    )
    assert (result.decision, result.severity) == (expected_decision, expected_severity)


def test_evaluator_is_deterministic_does_not_mutate_inputs_or_use_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs = BASE_INPUTS | {"data_quality_score": 79, "privacy_risk_score": 80}
    original = inputs.copy()

    def forbidden(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("publication domain gate attempted I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)

    first = domain_gate.evaluate_publication_readiness(**inputs)  # type: ignore[arg-type]
    second = domain_gate.evaluate_publication_readiness(**inputs)  # type: ignore[arg-type]

    assert first == second
    assert inputs == original


@pytest.mark.parametrize(
    ("quality", "privacy", "domain", "cli"),
    [
        (69, 0, "Needs Review", "Blocked"),
        (100, 60, "Needs Review", "Approved"),
        (100, 81, "Needs Review", "Blocked"),
    ],
)
def test_domain_and_cli_policies_are_intentionally_not_equivalent(
    quality: int, privacy: int, domain: str, cli: str
) -> None:
    domain_result = _evaluate(
        data_quality_score=quality,
        privacy_risk_score=privacy,
    )
    cli_result, _reason = evaluate_publication_gate(
        quality_score=quality,
        lgpd_risk_score=privacy,
        critical_issues=0,
    )

    assert domain_result.decision == domain
    assert cli_result == cli


@pytest.mark.parametrize(
    ("monitor_status", "expected_decision"),
    [("PASS", "Approved"), ("FAIL", "Needs Review")],
)
def test_monitor_step_policy_uses_only_monitoring_failures_and_never_blocks(
    monkeypatch: pytest.MonkeyPatch,
    monitor_status: str,
    expected_decision: str,
) -> None:
    monitoring_result = type(
        "MonitoringResult",
        (),
        {
            "check_name": "published_file_freshness_hours",
            "status": monitor_status,
        },
    )()
    captured: dict[str, object] = {}

    monkeypatch.setattr(platform_pipeline, "run_monitoring", lambda: [monitoring_result])
    monkeypatch.setattr(platform_pipeline, "save_published_monitoring_results", lambda _x: None)
    monkeypatch.setattr(platform_pipeline, "save_published_monitoring_report", lambda _x: None)
    monkeypatch.setattr(platform_pipeline, "load_published_monitoring_frame", lambda: __import__("pandas").DataFrame())
    monkeypatch.setattr(platform_pipeline, "load_governance_history", lambda: __import__("pandas").DataFrame())
    monkeypatch.setattr(platform_pipeline, "evaluate_governance_observability", lambda **_kwargs: [])
    monkeypatch.setattr(platform_pipeline, "save_observability_results", lambda _x: None)
    monkeypatch.setattr(
        platform_pipeline,
        "save_publication_decision_artifact",
        lambda **kwargs: captured.update(kwargs),
    )

    platform_pipeline._run_monitor_step()

    assert captured["publication_status"] == expected_decision
    assert captured["failed_checks_count"] == (0 if monitor_status == "PASS" else 1)
    assert captured["publication_status"] != "Blocked"
