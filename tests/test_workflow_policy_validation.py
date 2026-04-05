from __future__ import annotations

from pathlib import Path

from src.workflow_policy_validation import (
    WorkflowPolicyResult,
    render_workflow_policy_report,
    validate_workflow_contract,
)


def test_validate_workflow_contract_accepts_aligned_workflows(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "ci.yml").write_text(
        "name: CI\non:\n  push:\n    branches:\n      - \"**\"\n",
        encoding="utf-8",
    )

    contract = {
        "workflows": [
            {
                "name": "CI",
                "path": ".github/workflows/ci.yml",
                "push_branches": ["**"],
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
    report = render_workflow_policy_report([WorkflowPolicyResult(status="PASS", message="ok")])

    assert "| Status | Mensagem |" in report
    assert "`PASS`" in report
