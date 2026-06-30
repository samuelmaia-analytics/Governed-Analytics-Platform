from __future__ import annotations

from src.cloud_reference import (
    load_aws_reference_architecture,
    summarize_cost_controls,
)


def test_load_aws_reference_architecture_is_explicitly_not_provisioned() -> None:
    architecture = load_aws_reference_architecture()

    assert architecture.name == "aws_governed_analytics_reference"
    assert architecture.is_provisioned is False
    assert "storage" in architecture.service_names()
    assert "observability" in architecture.service_names()


def test_cost_controls_include_required_tags_and_guardrails() -> None:
    summary = summarize_cost_controls()

    assert summary["is_provisioned"] is False
    assert summary["required_tag_count"] >= 5
    assert summary["guardrail_count"] >= 5
    assert {
        guardrail["name"] for guardrail in summary["guardrails"]  # type: ignore[index]
    } >= {"monthly_budget", "athena_scan_limit", "idle_compute_shutdown"}
