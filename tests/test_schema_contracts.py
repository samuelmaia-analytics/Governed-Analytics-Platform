from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

import src.schema_contracts as schema_contracts
from src.schema_contracts import (
    ContractCheck,
    iter_contract_paths,
    load_contract,
    load_dataset,
    matches_expected_type,
    render_report,
    run_contract_checks,
    save_report,
    save_results,
    validate_contract,
)


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


def test_load_contract_iter_paths_and_load_dataset(tmp_path: Path, monkeypatch) -> None:
    contracts_dir = tmp_path / "contracts"
    curated_dir = contracts_dir / "curated"
    curated_dir.mkdir(parents=True)
    contract_path = curated_dir / "demo.contract.json"
    csv_path = tmp_path / "demo.csv"
    csv_path.write_text("id\n1\n", encoding="utf-8")
    contract_path.write_text(
        '{"dataset_name":"demo","layer":"published","path":"demo.csv","columns":{"id":"integer"}}',
        encoding="utf-8",
    )

    monkeypatch.setattr(schema_contracts, "CONTRACTS_DIR", contracts_dir)
    monkeypatch.setattr(schema_contracts, "ROOT_DIR", tmp_path)

    assert iter_contract_paths() == [contract_path]
    contract = load_contract(contract_path)
    dataset = load_dataset(contract)
    assert contract["dataset_name"] == "demo"
    assert list(dataset.columns) == ["id"]


def test_matches_expected_type_and_render_save_report(tmp_path: Path, monkeypatch) -> None:
    assert matches_expected_type(pd.Series([True, False]), "boolean") is True
    assert matches_expected_type(pd.Series([1.0, 2.0]), "float") is True
    assert matches_expected_type(pd.Series(pd.to_datetime(["2018-01-01"])), "datetime") is True

    checks = [
        ContractCheck(
            dataset_name="demo",
            layer="published",
            check_name="min_rows",
            status="PASS",
            details="ok",
        )
    ]
    monkeypatch.setattr(schema_contracts, "QUALITY_DIR", tmp_path / "quality")
    monkeypatch.setattr(schema_contracts, "DOCS_DIR", tmp_path / "docs")
    monkeypatch.setattr(schema_contracts, "RESULTS_PATH", tmp_path / "quality" / "schema_contract_results.csv")
    monkeypatch.setattr(schema_contracts, "REPORT_PATH", tmp_path / "docs" / "schema_contract_report.md")

    report = render_report(checks)
    results_path = save_results(checks)
    report_path = save_report(checks)

    assert "Relatorio de Contratos de Schema" in report
    assert results_path.exists()
    assert report_path.exists()


def test_run_contract_checks_and_main(tmp_path: Path, monkeypatch) -> None:
    contract_path = tmp_path / "demo.contract.json"
    contract_path.write_text("{}", encoding="utf-8")
    checks = [
        ContractCheck(
            dataset_name="demo",
            layer="published",
            check_name="missing_columns",
            status="PASS",
            details="ok",
        )
    ]
    monkeypatch.setattr(schema_contracts, "iter_contract_paths", lambda: [contract_path])
    monkeypatch.setattr(schema_contracts, "load_contract", lambda _path: {"dataset_name": "demo"})
    monkeypatch.setattr(schema_contracts, "validate_contract", lambda _contract: checks)
    monkeypatch.setattr(schema_contracts, "configure_logging", lambda: None)
    monkeypatch.setattr(schema_contracts, "QUALITY_DIR", tmp_path / "quality")
    monkeypatch.setattr(schema_contracts, "DOCS_DIR", tmp_path / "docs")
    monkeypatch.setattr(schema_contracts, "RESULTS_PATH", tmp_path / "quality" / "schema_contract_results.csv")
    monkeypatch.setattr(schema_contracts, "REPORT_PATH", tmp_path / "docs" / "schema_contract_report.md")

    result_checks = run_contract_checks()
    schema_contracts.main()

    assert result_checks == checks
    assert Path(schema_contracts.RESULTS_PATH).exists()
    assert Path(schema_contracts.REPORT_PATH).exists()
