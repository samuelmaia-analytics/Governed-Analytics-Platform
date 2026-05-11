from __future__ import annotations

from src.governance_validation import (
    GovernanceValidationResult,
    render_validation_report,
    validate_governance_contract,
)


def test_validate_governance_contract_accepts_aligned_contract() -> None:
    contract = {
        "branches": [
            {
                "name": "develop",
                "deployment_environment": "dev",
                "deployment_branch": "streamlit-dev",
            },
            {
                "name": "release",
                "deployment_environment": "stage",
                "deployment_branch": "streamlit-stage",
            },
            {
                "name": "main",
                "deployment_environment": "prod",
                "deployment_branch": "streamlit-prod",
            },
        ],
        "environments": [
            {
                "name": "streamlit-development",
                "target_environment": "dev",
                "deployment_branch": "streamlit-dev",
            },
            {
                "name": "streamlit-staging",
                "target_environment": "stage",
                "deployment_branch": "streamlit-stage",
            },
            {
                "name": "streamlit-production",
                "target_environment": "prod",
                "deployment_branch": "streamlit-prod",
            },
        ],
    }

    results = validate_governance_contract(contract)

    assert len(results) == 1
    assert results[0].status == "PASS"


def test_validate_governance_contract_flags_misalignment() -> None:
    contract = {
        "branches": [
            {
                "name": "main",
                "deployment_environment": "prod",
                "deployment_branch": "wrong-branch",
            }
        ],
        "environments": [],
    }

    results = validate_governance_contract(contract)

    assert any(result.status == "FAIL" for result in results)


def test_render_validation_report_includes_table() -> None:
    report = render_validation_report(
        [GovernanceValidationResult(status="PASS", message="ok")]
    )

    assert "| Status | Mensagem |" in report
    assert "`PASS`" in report
