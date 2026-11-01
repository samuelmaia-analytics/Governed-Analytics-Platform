from __future__ import annotations

from dataclasses import fields
from pathlib import Path

import pandas as pd
import pytest

import src.schema_contracts as contracts
from src.schema_contracts import ContractCheck


def test_contract_discovery_is_sorted_and_one_directory_deep(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "contracts"
    first = root / "a" / "first.contract.json"
    second = root / "b" / "second.contract.json"
    ignored = root / "deep" / "nested" / "ignored.contract.json"
    for path in [first, second, ignored]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(contracts, "CONTRACTS_DIR", root)

    assert contracts.iter_contract_paths() == [first, second]


def test_validate_contract_preserves_check_order_and_failure_details(monkeypatch) -> None:
    df = pd.DataFrame({"id": [1, 1], "extra": ["x", "y"]})
    contract = {
        "dataset_name": "demo",
        "layer": "curated",
        "path": "unused.parquet",
        "columns": {"id": "string", "missing": "float"},
        "allow_unexpected_columns": False,
        "min_rows": 3,
        "primary_key": ["id"],
    }
    monkeypatch.setattr(contracts, "load_dataset", lambda _contract: df)

    checks = contracts.validate_contract(contract)

    assert [check.check_name for check in checks] == [
        "missing_columns",
        "unexpected_columns",
        "type__id",
        "min_rows",
        "primary_key_duplicates",
    ]
    assert [check.status for check in checks] == ["FAIL"] * 5
    assert checks[0].details == "Ausentes: ['missing']"
    assert checks[1].details == "Inesperadas: ['extra']"
    assert checks[-1].details == "Chave=['id'] | duplicados=2"
    assert [field.name for field in fields(ContractCheck)] == [
        "dataset_name",
        "layer",
        "check_name",
        "status",
        "details",
    ]


def test_invalid_contract_and_missing_dataset_errors_are_propagated(
    tmp_path: Path, monkeypatch
) -> None:
    invalid = tmp_path / "invalid.contract.json"
    invalid.write_text("{invalid", encoding="utf-8")
    monkeypatch.setattr(contracts, "ROOT_DIR", tmp_path)

    with pytest.raises(ValueError):
        contracts.load_contract(invalid)
    with pytest.raises(FileNotFoundError):
        contracts.load_dataset({"path": "missing.csv"})
    with pytest.raises(ValueError, match="Formato nao suportado"):
        contracts.load_dataset({"path": "dataset.txt"})


def test_schema_contract_public_runners_remain_importable() -> None:
    assert all(
        callable(api)
        for api in [
            contracts.iter_contract_paths,
            contracts.load_contract,
            contracts.load_dataset,
            contracts.validate_contract,
            contracts.run_contract_checks,
            contracts.save_results,
            contracts.render_report,
            contracts.save_report,
        ]
    )
