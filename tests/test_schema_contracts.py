from __future__ import annotations

from datetime import date

import pandas as pd

from src.schema_contracts import matches_expected_type, validate_contract


def test_matches_expected_type_supports_date_like_objects() -> None:
    series = pd.Series([date(2018, 1, 1), date(2018, 1, 2), None], dtype="object")

    assert matches_expected_type(series, "date_like") is True


def test_validate_contract_flags_missing_columns_and_duplicate_primary_key() -> None:
    contract = {
        "dataset_name": "demo_dataset",
        "layer": "published",
        "path": "unused.parquet",
        "min_rows": 2,
        "primary_key": ["order_id", "order_item_id"],
        "allow_unexpected_columns": False,
        "columns": {
            "order_id": "string",
            "order_item_id": "integer",
            "missing_col": "string",
        },
    }

    df = pd.DataFrame(
        {
            "order_id": ["a", "a"],
            "order_item_id": [1, 1],
        }
    )

    import src.schema_contracts as schema_contracts

    original_loader = schema_contracts.load_dataset
    schema_contracts.load_dataset = lambda _: df
    try:
        checks = validate_contract(contract)
    finally:
        schema_contracts.load_dataset = original_loader

    checks_by_name = {check.check_name: check for check in checks}
    assert checks_by_name["missing_columns"].status == "FAIL"
    assert checks_by_name["primary_key_duplicates"].status == "FAIL"
