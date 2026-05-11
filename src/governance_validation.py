from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ROOT_DIR
from src.release_management import DEPLOYMENT_PROFILES

DEFAULT_GOVERNANCE_CONTRACT_PATH = (
    ROOT_DIR / "contracts" / "governance" / "release_governance.json"
)


@dataclass(frozen=True)
class GovernanceValidationResult:
    status: str
    message: str


def load_governance_contract(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_governance_contract(
    contract: dict[str, Any],
) -> list[GovernanceValidationResult]:
    results: list[GovernanceValidationResult] = []
    branches = contract.get("branches", [])
    environments = contract.get("environments", [])

    branch_by_environment = {
        branch["deployment_environment"]: branch
        for branch in branches
        if isinstance(branch, dict)
    }
    environment_by_target = {
        environment["target_environment"]: environment
        for environment in environments
        if isinstance(environment, dict)
    }

    for environment_name, profile in DEPLOYMENT_PROFILES.items():
        branch = branch_by_environment.get(environment_name)
        if branch is None:
            results.append(
                GovernanceValidationResult(
                    "FAIL", f"Branch policy ausente para `{environment_name}`."
                )
            )
            continue
        if branch.get("name") != profile.source_branch:
            results.append(
                GovernanceValidationResult(
                    "FAIL",
                    f"Branch `{environment_name}` divergente: esperado source branch `{profile.source_branch}`.",
                )
            )
        if branch.get("deployment_branch") != profile.deployment_branch:
            results.append(
                GovernanceValidationResult(
                    "FAIL",
                    f"Deploy branch divergente para `{environment_name}`: esperado `{profile.deployment_branch}`.",
                )
            )

        environment = environment_by_target.get(environment_name)
        if environment is None:
            results.append(
                GovernanceValidationResult(
                    "FAIL", f"GitHub environment ausente para `{environment_name}`."
                )
            )
            continue
        if environment.get("name") != profile.github_environment:
            results.append(
                GovernanceValidationResult(
                    "FAIL",
                    f"GitHub environment divergente para `{environment_name}`: esperado `{profile.github_environment}`.",
                )
            )
        if environment.get("deployment_branch") != profile.deployment_branch:
            results.append(
                GovernanceValidationResult(
                    "FAIL",
                    f"Environment `{environment_name}` aponta para deploy branch incorreta.",
                )
            )

    if not results:
        results.append(
            GovernanceValidationResult(
                "PASS", "Contrato de governança alinhado aos perfis de release."
            )
        )
    return results


def render_validation_report(results: list[GovernanceValidationResult]) -> str:
    lines = [
        "# Validação de Governança de Release",
        "",
        "| Status | Mensagem |",
        "| --- | --- |",
    ]
    for result in results:
        lines.append(f"| `{result.status}` | {result.message} |")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida o contrato versionado de governança de release."
    )
    parser.add_argument(
        "--contract", type=Path, default=DEFAULT_GOVERNANCE_CONTRACT_PATH
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contract = load_governance_contract(args.contract.resolve())
    results = validate_governance_contract(contract)
    report = render_validation_report(results)
    print(report)
    if any(result.status == "FAIL" for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
