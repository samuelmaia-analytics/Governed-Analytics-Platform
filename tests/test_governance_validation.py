from __future__ import annotations

import json

import pytest

import src.governance_validation as gv
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


def test_main_passes_with_aligned_contract(tmp_path, monkeypatch, capsys) -> None:
    contract = {
        "branches": [
            {"name": "develop", "deployment_environment": "dev", "deployment_branch": "streamlit-dev"},
            {"name": "release", "deployment_environment": "stage", "deployment_branch": "streamlit-stage"},
            {"name": "main", "deployment_environment": "prod", "deployment_branch": "streamlit-prod"},
        ],
        "environments": [
            {"name": "streamlit-development", "target_environment": "dev", "deployment_branch": "streamlit-dev"},
            {"name": "streamlit-staging", "target_environment": "stage", "deployment_branch": "streamlit-stage"},
            {"name": "streamlit-production", "target_environment": "prod", "deployment_branch": "streamlit-prod"},
        ],
    }
    contract_file = tmp_path / "governance.json"
    contract_file.write_text(json.dumps(contract), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["governance_validation.py", "--contract", str(contract_file)])

    gv.main()

    assert "PASS" in capsys.readouterr().out


def test_main_exits_with_error_on_misaligned_contract(tmp_path, monkeypatch) -> None:
    contract = {"branches": [{"name": "wrong", "deployment_environment": "prod", "deployment_branch": "x"}], "environments": []}
    contract_file = tmp_path / "governance.json"
    contract_file.write_text(json.dumps(contract), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["governance_validation.py", "--contract", str(contract_file)])

    with pytest.raises(SystemExit) as exc_info:
        gv.main()

    assert exc_info.value.code == 1
