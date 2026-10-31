from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
    is_string_dtype,
)

from src.schema_contract_components.models import ContractCheck

LoadDatasetFn = Callable[[dict[str, Any]], pd.DataFrame]
ContractPathsFn = Callable[[], list[Any]]
LoadContractFn = Callable[[Any], dict[str, Any]]
ValidateContractFn = Callable[[dict[str, Any]], list[ContractCheck]]


def matches_expected_type(series: pd.Series, expected_type: str) -> bool:
    if expected_type == "string":
        return is_string_dtype(series.dtype) or is_object_dtype(series.dtype)
    if expected_type == "integer":
        return is_integer_dtype(series.dtype)
    if expected_type == "float":
        return is_float_dtype(series.dtype) or is_integer_dtype(series.dtype)
    if expected_type == "boolean":
        return is_bool_dtype(series.dtype)
    if expected_type == "datetime":
        return is_datetime64_any_dtype(series.dtype)
    if expected_type == "date_like":
        if is_datetime64_any_dtype(series.dtype):
            return True
        if not is_object_dtype(series.dtype):
            return False
        non_null = series.dropna()
        return non_null.empty or all(
            hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day")
            for value in non_null
        )
    raise ValueError(f"Tipo esperado desconhecido: {expected_type}")


def validate_contract(
    contract: dict[str, Any], *, load_dataset_fn: LoadDatasetFn
) -> list[ContractCheck]:
    dataset_name = str(contract["dataset_name"])
    layer = str(contract["layer"])
    df = load_dataset_fn(contract)
    checks: list[ContractCheck] = []

    expected_columns = set(contract["columns"].keys())
    actual_columns = set(df.columns)
    missing_columns = sorted(expected_columns - actual_columns)
    checks.append(
        ContractCheck(
            dataset_name=dataset_name,
            layer=layer,
            check_name="missing_columns",
            status="PASS" if not missing_columns else "FAIL",
            details=f"Ausentes: {missing_columns if missing_columns else 'nenhuma'}",
        )
    )

    if not bool(contract.get("allow_unexpected_columns", False)):
        unexpected_columns = sorted(actual_columns - expected_columns)
        checks.append(
            ContractCheck(
                dataset_name=dataset_name,
                layer=layer,
                check_name="unexpected_columns",
                status="PASS" if not unexpected_columns else "FAIL",
                details=f"Inesperadas: {unexpected_columns if unexpected_columns else 'nenhuma'}",
            )
        )

    for column, expected_type in contract["columns"].items():
        if column not in df.columns:
            continue
        matches = matches_expected_type(df[column], str(expected_type))
        checks.append(
            ContractCheck(
                dataset_name=dataset_name,
                layer=layer,
                check_name=f"type__{column}",
                status="PASS" if matches else "FAIL",
                details=f"Esperado={expected_type} | atual={df[column].dtype}",
            )
        )

    min_rows = int(contract.get("min_rows", 0))
    checks.append(
        ContractCheck(
            dataset_name=dataset_name,
            layer=layer,
            check_name="min_rows",
            status="PASS" if len(df) >= min_rows else "FAIL",
            details=f"Linhas observadas={len(df)} | minimo={min_rows}",
        )
    )

    primary_key = list(contract.get("primary_key", []))
    if primary_key:
        duplicate_count = int(df.duplicated(subset=primary_key, keep=False).sum())
        checks.append(
            ContractCheck(
                dataset_name=dataset_name,
                layer=layer,
                check_name="primary_key_duplicates",
                status="PASS" if duplicate_count == 0 else "FAIL",
                details=f"Chave={primary_key} | duplicados={duplicate_count}",
            )
        )

    return checks


def run_contract_checks(
    *,
    contract_paths_fn: ContractPathsFn,
    load_contract_fn: LoadContractFn,
    validate_contract_fn: ValidateContractFn,
) -> list[ContractCheck]:
    checks: list[ContractCheck] = []
    for contract_path in contract_paths_fn():
        contract = load_contract_fn(contract_path)
        checks.extend(validate_contract_fn(contract))
    return checks
