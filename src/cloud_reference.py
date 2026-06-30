from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.config import ROOT_DIR

DEFAULT_AWS_REFERENCE_PATH = ROOT_DIR / "config" / "aws_reference_architecture.yml"


@dataclass(frozen=True)
class CostGuardrail:
    name: str
    control: str


@dataclass(frozen=True)
class AwsReferenceArchitecture:
    name: str
    status: str
    portfolio_boundary: str
    services: dict[str, dict[str, Any]]
    required_tags: tuple[str, ...]
    cost_guardrails: tuple[CostGuardrail, ...]

    @property
    def is_provisioned(self) -> bool:
        return self.status.lower() not in {
            "reference_architecture_not_provisioned",
            "simulated",
            "design_only",
        }

    def service_names(self) -> tuple[str, ...]:
        return tuple(sorted(self.services))


def load_aws_reference_architecture(
    config_path: Path = DEFAULT_AWS_REFERENCE_PATH,
) -> AwsReferenceArchitecture:
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    architecture = config["architecture"]
    cost_controls = config.get("cost_controls", {})
    return AwsReferenceArchitecture(
        name=str(architecture["name"]),
        status=str(architecture["status"]),
        portfolio_boundary=str(architecture["portfolio_boundary"]).strip(),
        services=dict(config.get("services", {})),
        required_tags=tuple(str(tag) for tag in cost_controls.get("required_tags", [])),
        cost_guardrails=tuple(
            CostGuardrail(name=str(item["name"]), control=str(item["control"]))
            for item in cost_controls.get("guardrails", [])
        ),
    )


def summarize_cost_controls(
    architecture: AwsReferenceArchitecture | None = None,
) -> dict[str, object]:
    aws_architecture = architecture or load_aws_reference_architecture()
    return {
        "architecture": aws_architecture.name,
        "status": aws_architecture.status,
        "is_provisioned": aws_architecture.is_provisioned,
        "required_tag_count": len(aws_architecture.required_tags),
        "guardrail_count": len(aws_architecture.cost_guardrails),
        "guardrails": [
            {"name": guardrail.name, "control": guardrail.control}
            for guardrail in aws_architecture.cost_guardrails
        ],
    }
