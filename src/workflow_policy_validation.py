from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ROOT_DIR
from src.governance_validation import (
    DEFAULT_GOVERNANCE_CONTRACT_PATH,
    load_governance_contract,
)


@dataclass(frozen=True)
class WorkflowPolicyResult:
    status: str
    message: str


def load_workflow_definition(path: Path) -> dict[str, Any]:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def _normalize_branches(branches: list[Any] | None) -> list[str]:
    if not branches:
        return []
    return [str(branch).strip() for branch in branches]


def validate_workflow_contract(
    contract: dict[str, Any], root_dir: Path = ROOT_DIR
) -> list[WorkflowPolicyResult]:
    results: list[WorkflowPolicyResult] = []
    workflow_specs = contract.get("workflows", [])

    for spec in workflow_specs:
        workflow_path = root_dir / str(spec["path"])
        if not workflow_path.exists():
            results.append(
                WorkflowPolicyResult("FAIL", f"Workflow ausente: `{spec['path']}`.")
            )
            continue

        workflow = load_workflow_definition(workflow_path)
        workflow_name = str(workflow.get("name", ""))
        if workflow_name != spec["name"]:
            results.append(
                WorkflowPolicyResult(
                    "FAIL",
                    f"Nome divergente em `{spec['path']}`: esperado `{spec['name']}`, obtido `{workflow_name}`.",
                )
            )

        on_section = workflow.get("on", {})
        push_section = (
            on_section.get("push", {}) if isinstance(on_section, dict) else {}
        )
        workflow_run_section = (
            on_section.get("workflow_run", {}) if isinstance(on_section, dict) else {}
        )

        expected_push_branches = _normalize_branches(spec.get("push_branches"))
        if expected_push_branches:
            actual_push_branches = (
                _normalize_branches(push_section.get("branches"))
                if isinstance(push_section, dict)
                else []
            )
            if actual_push_branches != expected_push_branches:
                results.append(
                    WorkflowPolicyResult(
                        "FAIL",
                        f"Push branches divergentes em `{spec['path']}`: esperado {expected_push_branches}, obtido {actual_push_branches}.",
                    )
                )

        expected_workflow_run_workflows = _normalize_branches(
            spec.get("workflow_run_workflows")
        )
        if expected_workflow_run_workflows:
            actual_workflow_run_workflows = (
                _normalize_branches(workflow_run_section.get("workflows"))
                if isinstance(workflow_run_section, dict)
                else []
            )
            if actual_workflow_run_workflows != expected_workflow_run_workflows:
                results.append(
                    WorkflowPolicyResult(
                        "FAIL",
                        f"workflow_run.workflows divergente em `{spec['path']}`: esperado {expected_workflow_run_workflows}, obtido {actual_workflow_run_workflows}.",
                    )
                )

        expected_workflow_run_branches = _normalize_branches(
            spec.get("workflow_run_branches")
        )
        if expected_workflow_run_branches:
            actual_workflow_run_branches = (
                _normalize_branches(workflow_run_section.get("branches"))
                if isinstance(workflow_run_section, dict)
                else []
            )
            if actual_workflow_run_branches != expected_workflow_run_branches:
                results.append(
                    WorkflowPolicyResult(
                        "FAIL",
                        f"workflow_run.branches divergente em `{spec['path']}`: esperado {expected_workflow_run_branches}, obtido {actual_workflow_run_branches}.",
                    )
                )

    if not results:
        results.append(
            WorkflowPolicyResult(
                "PASS", "Workflows alinhados ao contrato de governança."
            )
        )
    return results


def render_workflow_policy_report(results: list[WorkflowPolicyResult]) -> str:
    lines = [
        "# Validação de Política de Workflows",
        "",
        "| Status | Mensagem |",
        "| --- | --- |",
    ]
    for result in results:
        lines.append(f"| `{result.status}` | {result.message} |")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida workflows do GitHub Actions contra o contrato de governança."
    )
    parser.add_argument(
        "--contract", type=Path, default=DEFAULT_GOVERNANCE_CONTRACT_PATH
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contract = load_governance_contract(args.contract.resolve())
    results = validate_workflow_contract(contract)
    report = render_workflow_policy_report(results)
    print(report)
    if any(result.status == "FAIL" for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
