from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DeploymentProfile:
    environment: str
    source_branch: str
    deployment_branch: str
    github_environment: str


@dataclass(frozen=True)
class PromotionPlan:
    target_environment: str
    source_ref: str
    source_branch: str
    deployment_branch: str
    github_environment: str


DEPLOYMENT_PROFILES: dict[str, DeploymentProfile] = {
    "dev": DeploymentProfile(
        environment="dev",
        source_branch="develop",
        deployment_branch="streamlit-dev",
        github_environment="streamlit-development",
    ),
    "stage": DeploymentProfile(
        environment="stage",
        source_branch="release",
        deployment_branch="streamlit-stage",
        github_environment="streamlit-staging",
    ),
    "prod": DeploymentProfile(
        environment="prod",
        source_branch="main",
        deployment_branch="streamlit-prod",
        github_environment="streamlit-production",
    ),
}


def normalize_source_branch(source_branch: str) -> str:
    normalized = source_branch.removeprefix("refs/heads/").strip()
    return "main" if normalized == "master" else normalized


def resolve_promotion_plan(
    target_environment: str, source_ref: str, source_branch: str
) -> PromotionPlan:
    profile = DEPLOYMENT_PROFILES.get(target_environment)
    if profile is None:
        raise ValueError(f"Ambiente de deploy inválido: {target_environment}")

    normalized_branch = normalize_source_branch(source_branch)
    if normalized_branch != profile.source_branch:
        raise ValueError(
            f"Ambiente `{target_environment}` exige source branch `{profile.source_branch}`, "
            f"mas recebeu `{normalized_branch}`."
        )

    return PromotionPlan(
        target_environment=profile.environment,
        source_ref=source_ref,
        source_branch=normalized_branch,
        deployment_branch=profile.deployment_branch,
        github_environment=profile.github_environment,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve plano de promoção entre ambientes de deploy."
    )
    parser.add_argument(
        "--target-environment",
        choices=sorted(DEPLOYMENT_PROFILES.keys()),
        required=True,
    )
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--source-branch", required=True)
    parser.add_argument(
        "--github-output",
        help="Arquivo de output do GitHub Actions para exportar o plano.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = resolve_promotion_plan(
        args.target_environment, args.source_ref, args.source_branch
    )
    payload = json.dumps(asdict(plan), ensure_ascii=False)
    print(payload)
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as handle:
            handle.write(f"plan={payload}\n")
            handle.write(f"deployment_branch={plan.deployment_branch}\n")
            handle.write(f"github_environment={plan.github_environment}\n")
            handle.write(f"target_environment={plan.target_environment}\n")


if __name__ == "__main__":
    main()
