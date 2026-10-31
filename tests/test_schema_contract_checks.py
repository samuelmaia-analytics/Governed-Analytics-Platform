from __future__ import annotations

import pandas as pd
import pytest

from src.schema_contract_components import checks
from src.schema_contract_components.models import ContractCheck


def test_validation_preserves_check_order_structure_and_failures() -> None:
    df = pd.DataFrame({"id": [1, 1], "extra": ["x", "y"]})
    contract = {
        "dataset_name": "demo",
        "layer": "curated",
        "columns": {"id": "string", "missing": "float"},
        "allow_unexpected_columns": False,
        "min_rows": 3,
        "primary_key": ["id"],
    }

    results = checks.validate_contract(contract, load_dataset_fn=lambda _contract: df)

    assert all(isinstance(result, ContractCheck) for result in results)
    assert [result.check_name for result in results] == [
        "missing_columns",
        "unexpected_columns",
        "type__id",
        "min_rows",
        "primary_key_duplicates",
    ]
    assert [result.status for result in results] == ["FAIL"] * 5
    assert results[-1].details == "Chave=['id'] | duplicados=2"


def test_expected_types_preserve_current_semantics() -> None:
    assert checks.matches_expected_type(pd.Series(["a"]), "string")
    assert checks.matches_expected_type(pd.Series([1]), "integer")
    assert checks.matches_expected_type(pd.Series([1]), "float")
    assert checks.matches_expected_type(pd.Series([True]), "boolean")
    assert checks.matches_expected_type(
        pd.Series(pd.to_datetime(["2020-01-01"])), "datetime"
    )
    with pytest.raises(ValueError, match="Tipo esperado desconhecido"):
        checks.matches_expected_type(pd.Series([1]), "decimal")


def test_runner_uses_injected_operations_in_contract_order() -> None:
    paths = ["b.json", "a.json"]
    events: list[tuple[str, object]] = []

    def load(path):
        events.append(("load", path))
        return {"dataset_name": path}

    def validate(contract):
        events.append(("validate", contract))
        return [ContractCheck(contract["dataset_name"], "x", "check", "PASS", "ok")]

    results = checks.run_contract_checks(
        contract_paths_fn=lambda: paths,
        load_contract_fn=load,
        validate_contract_fn=validate,
    )

    assert [result.dataset_name for result in results] == paths
    assert [event[0] for event in events] == ["load", "validate", "load", "validate"]
