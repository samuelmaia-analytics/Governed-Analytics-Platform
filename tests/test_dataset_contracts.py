from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CONTRACTS_ROOT = Path("contracts")
DATASET_CONTRACT_GLOB = "*.contract.yml"

REQUIRED_DATASET_FIELDS = {
    "dataset_name",
    "owner",
    "domain",
    "description",
    "grain",
    "primary_key",
    "freshness_sla",
    "privacy_classification",
    "columns",
    "lineage",
    "publication_policy",
}

REQUIRED_COLUMN_FIELDS = {
    "name",
    "type",
    "nullable",
    "description",
    "classification",
}

REQUIRED_PUBLICATION_POLICY_FIELDS = {
    "minimum_quality_score",
    "maximum_privacy_risk_score",
    "freshness_requirement",
    "contract_required",
    "blocking_conditions",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(content, dict), f"{path} must contain a YAML object."
    return content


def _dataset_contract_paths() -> list[Path]:
    return sorted(CONTRACTS_ROOT.rglob(DATASET_CONTRACT_GLOB))


def test_dataset_contract_yaml_files_exist() -> None:
    paths = _dataset_contract_paths()
    assert paths, (
        "No dataset YAML contracts found (expected at least one *.contract.yml)."
    )


def test_dataset_contract_required_top_level_fields() -> None:
    for path in _dataset_contract_paths():
        contract = _load_yaml(path)
        missing = REQUIRED_DATASET_FIELDS - set(contract.keys())
        assert not missing, (
            f"{path} missing required top-level fields: {sorted(missing)}"
        )


def test_dataset_contract_columns_structure() -> None:
    for path in _dataset_contract_paths():
        contract = _load_yaml(path)
        columns = contract["columns"]
        assert isinstance(columns, list), f"{path} columns must be a list."
        assert columns, f"{path} columns must not be empty."
        for idx, column in enumerate(columns):
            assert isinstance(column, dict), f"{path} columns[{idx}] must be an object."
            missing = REQUIRED_COLUMN_FIELDS - set(column.keys())
            assert not missing, (
                f"{path} columns[{idx}] missing required fields: {sorted(missing)}"
            )


def test_dataset_contract_lineage_structure() -> None:
    for path in _dataset_contract_paths():
        contract = _load_yaml(path)
        lineage = contract["lineage"]
        assert isinstance(lineage, dict), f"{path} lineage must be an object."
        assert "upstream" in lineage, f"{path} lineage must include upstream."
        assert "downstream" in lineage, f"{path} lineage must include downstream."
        assert isinstance(lineage["upstream"], list), (
            f"{path} lineage.upstream must be a list."
        )
        assert isinstance(lineage["downstream"], list), (
            f"{path} lineage.downstream must be a list."
        )


def test_dataset_contract_publication_policy_fields() -> None:
    for path in _dataset_contract_paths():
        contract = _load_yaml(path)
        policy = contract["publication_policy"]
        assert isinstance(policy, dict), f"{path} publication_policy must be an object."
        missing = REQUIRED_PUBLICATION_POLICY_FIELDS - set(policy.keys())
        assert not missing, (
            f"{path} publication_policy missing required fields: {sorted(missing)}"
        )
