from __future__ import annotations

import json
from pathlib import Path

import pytest

import src.workflow_policy_validation as wpv
from src.workflow_policy_validation import (
    WorkflowPolicyResult,
    render_workflow_policy_report,
    validate_workflow_contract,
)


def test_validate_workflow_contract_accepts_aligned_workflows(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "ci.yml").write_text(
        "name: CI\non:\n  push:\n    branches:\n      - develop\n      - release\n      - main\n      - master\n",
        encoding="utf-8",
    )

    contract = {
        "workflows": [
            {
                "name": "CI",
                "path": ".github/workflows/ci.yml",
                "push_branches": ["develop", "release", "main", "master"],
            }
        ]
    }

    results = validate_workflow_contract(contract, root_dir=tmp_path)

    assert len(results) == 1
    assert results[0].status == "PASS"


def test_validate_workflow_contract_flags_trigger_misalignment(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "deploy.yml").write_text(
        "name: Deploy Streamlit\non:\n  workflow_run:\n    workflows:\n      - Lint\n    branches:\n      - release\n",
        encoding="utf-8",
    )

    contract = {
        "workflows": [
            {
                "name": "Deploy Streamlit",
                "path": ".github/workflows/deploy.yml",
                "workflow_run_workflows": ["CI"],
                "workflow_run_branches": ["main", "master"],
            }
        ]
    }

    results = validate_workflow_contract(contract, root_dir=tmp_path)

    assert any(result.status == "FAIL" for result in results)


def test_render_workflow_policy_report_includes_table() -> None:
    report = render_workflow_policy_report(
        [WorkflowPolicyResult(status="PASS", message="ok")]
    )

    assert "| Status | Mensagem |" in report
    assert "`PASS`" in report


def test_validate_workflow_contract_flags_missing_workflow_file(tmp_path: Path) -> None:
    contract = {"workflows": [{"name": "CI", "path": ".github/workflows/missing.yml"}]}
    results = validate_workflow_contract(contract, root_dir=tmp_path)
    assert any(result.status == "FAIL" for result in results)
    assert any("ausente" in r.message for r in results)


def test_main_passes_with_aligned_contract(tmp_path: Path, monkeypatch, capsys) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "ci.yml").write_text(
        "name: CI\non:\n  push:\n    branches:\n      - main\n",
        encoding="utf-8",
    )
    contract = {
        "workflows": [{"name": "CI", "path": ".github/workflows/ci.yml", "push_branches": ["main"]}]
    }
    contract_file = tmp_path / "release_governance.json"
    contract_file.write_text(json.dumps(contract), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["workflow_policy_validation.py", "--contract", str(contract_file)])
    original_validate = wpv.validate_workflow_contract
    monkeypatch.setattr(
        wpv, "validate_workflow_contract",
        lambda c, root_dir=tmp_path: original_validate(c, root_dir=tmp_path),
    )

    wpv.main()

    assert "PASS" in capsys.readouterr().out


def test_main_exits_on_misaligned_workflow(tmp_path: Path, monkeypatch) -> None:
    contract = {"workflows": [{"name": "CI", "path": ".github/workflows/nonexistent.yml"}]}
    contract_file = tmp_path / "release_governance.json"
    contract_file.write_text(json.dumps(contract), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["workflow_policy_validation.py", "--contract", str(contract_file)])
    monkeypatch.setattr(wpv, "ROOT_DIR", tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        wpv.main()

    assert exc_info.value.code == 1
