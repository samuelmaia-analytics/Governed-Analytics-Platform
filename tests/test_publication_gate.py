from __future__ import annotations

import pytest

from scripts.run_publication_gate import evaluate_publication_gate
from src.publication_gate import evaluate_publication_readiness


def test_approved_dataset() -> None:
    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=20,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert result.decision == "Approved"
    assert result.severity == "Low"
    assert result.reasons
    assert result.required_actions


def test_blocked_by_critical_rule_failures() -> None:
    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=20,
        critical_rule_failures=2,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert result.decision == "Blocked"
    assert result.severity == "Critical"
    assert any("Critical rule failures" in reason for reason in result.reasons)


def test_blocked_by_unprotected_sensitive_data() -> None:
    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=20,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=True,
    )
    assert result.decision == "Blocked"
    assert result.severity == "Critical"
    assert any(
        "Sensitive data found without masking/anonymization" in reason
        for reason in result.reasons
    )


def test_blocked_by_failed_schema_contract() -> None:
    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=20,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="failed",
        has_sensitive_data_without_protection=False,
    )
    assert result.decision == "Blocked"
    assert result.severity == "Critical"
    assert any(
        "Schema contract validation failed" in reason for reason in result.reasons
    )


def test_needs_review_low_data_quality_score() -> None:
    result = evaluate_publication_readiness(
        data_quality_score=70,
        privacy_risk_score=20,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert result.decision == "Needs Review"
    assert result.severity == "Medium"
    assert any(
        "Data quality score below recommended threshold" in reason
        for reason in result.reasons
    )


def test_needs_review_elevated_privacy_risk_score() -> None:
    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=65,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert result.decision == "Needs Review"
    assert result.severity == "Medium"
    assert any("Privacy risk score is elevated" in reason for reason in result.reasons)


def test_needs_review_warning_or_stale_freshness_status() -> None:
    warning_result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=20,
        critical_rule_failures=0,
        freshness_status="warning",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    stale_result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=20,
        critical_rule_failures=0,
        freshness_status="stale",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )

    assert warning_result.decision == "Needs Review"
    assert stale_result.decision == "Needs Review"
    assert warning_result.severity == "Medium"
    assert stale_result.severity == "High"
    assert any(
        "Freshness status requires attention" in reason
        for reason in warning_result.reasons
    )
    assert any(
        "Freshness status requires attention" in reason
        for reason in stale_result.reasons
    )


def test_returned_object_contains_required_fields() -> None:
    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=20,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert hasattr(result, "decision")
    assert hasattr(result, "severity")
    assert hasattr(result, "reasons")
    assert hasattr(result, "required_actions")


def test_cli_publication_gate_rules_cover_approved_review_and_blocked() -> None:
    assert (
        evaluate_publication_gate(
            quality_score=92,
            lgpd_risk_score=45,
            critical_issues=0,
        )[0]
        == "Approved"
    )
    assert (
        evaluate_publication_gate(
            quality_score=75,
            lgpd_risk_score=70,
            critical_issues=0,
        )[0]
        == "Needs Review"
    )
    assert (
        evaluate_publication_gate(
            quality_score=60,
            lgpd_risk_score=85,
            critical_issues=2,
        )[0]
        == "Blocked"
    )


@pytest.mark.parametrize("field,value", [
    ("data_quality_score", float("nan")),
    ("data_quality_score", float("inf")),
    ("data_quality_score", -1),
    ("data_quality_score", 101),
    ("data_quality_score", "95"),
    ("data_quality_score", True),
    ("privacy_risk_score", float("nan")),
    ("privacy_risk_score", float("-inf")),
    ("privacy_risk_score", -1),
    ("privacy_risk_score", 101),
    ("privacy_risk_score", None),
    ("critical_rule_failures", -1),
    ("critical_rule_failures", 0.5),
    ("critical_rule_failures", False),
    ("critical_rule_failures", None),
    ("freshness_status", "unknown"),
    ("freshness_status", None),
    ("schema_contract_status", "unknown"),
    ("schema_contract_status", None),
    ("has_sensitive_data_without_protection", "false"),
    ("has_sensitive_data_without_protection", 0),
    ("has_sensitive_data_without_protection", None),
])
def test_invalid_evidence_cannot_be_approved(field, value):
    evidence = dict(
        data_quality_score=95, privacy_risk_score=20,
        critical_rule_failures=0, freshness_status="fresh",
        schema_contract_status="passed", has_sensitive_data_without_protection=False,
    )
    evidence[field] = value
    with pytest.raises(ValueError):
        evaluate_publication_readiness(**evidence)


@pytest.mark.parametrize("quality,privacy,expected", [
    (100, 0, "Approved"), (80, 59.5, "Approved"),
    (79.9, 0, "Needs Review"), (100, 60, "Needs Review"),
    (0, 100, "Needs Review"),
])
def test_valid_score_boundaries(quality, privacy, expected):
    result = evaluate_publication_readiness(
        data_quality_score=quality, privacy_risk_score=privacy,
        critical_rule_failures=0, freshness_status="fresh",
        schema_contract_status="passed", has_sensitive_data_without_protection=False,
    )
    assert result.decision == expected
