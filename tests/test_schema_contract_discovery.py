from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.schema_contract_components import discovery


def test_discovery_preserves_glob_depth_and_sorted_order(tmp_path: Path) -> None:
    contracts_dir = tmp_path / "contracts"
    expected = [
        contracts_dir / "a" / "first.contract.json",
        contracts_dir / "b" / "second.contract.json",
    ]
    ignored = contracts_dir / "nested" / "deep" / "ignored.contract.json"
    for path in [expected[1], expected[0], ignored]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")

    assert discovery.iter_contract_paths(contracts_dir) == expected


def test_load_contract_preserves_json_parsing_and_invalid_error(tmp_path: Path) -> None:
    valid = tmp_path / "valid.json"
    invalid = tmp_path / "invalid.json"
    valid.write_text('{"dataset_name": "demo"}', encoding="utf-8")
    invalid.write_text("{invalid", encoding="utf-8")

    assert discovery.load_contract(valid) == {"dataset_name": "demo"}
    with pytest.raises(ValueError):
        discovery.load_contract(invalid)


def test_load_dataset_reads_supported_formats_and_propagates_missing(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "dataset.csv"
    parquet_path = tmp_path / "dataset.parquet"
    expected = pd.DataFrame({"id": [1]})
    expected.to_csv(csv_path, index=False)
    expected.to_parquet(parquet_path, index=False)

    pd.testing.assert_frame_equal(
        discovery.load_dataset({"path": "dataset.csv"}, root_dir=tmp_path), expected
    )
    pd.testing.assert_frame_equal(
        discovery.load_dataset({"path": "dataset.parquet"}, root_dir=tmp_path),
        expected,
    )
    with pytest.raises(FileNotFoundError):
        discovery.load_dataset({"path": "missing.csv"}, root_dir=tmp_path)
    with pytest.raises(ValueError, match="Formato nao suportado"):
        discovery.load_dataset({"path": "dataset.txt"}, root_dir=tmp_path)
