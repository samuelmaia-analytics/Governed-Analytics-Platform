from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import infer_dataset_name, load_dataset


def test_load_dataset_reads_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({"a": [1], "b": ["x"]}).to_csv(csv_path, index=False)

    loaded = load_dataset(csv_path)

    assert loaded.shape == (1, 2)
    assert loaded.loc[0, "a"] == 1


def test_load_dataset_reads_parquet(tmp_path: Path) -> None:
    parquet_path = tmp_path / "sample.parquet"
    pd.DataFrame({"a": [1, 2]}).to_parquet(parquet_path, index=False)

    loaded = load_dataset(parquet_path)

    assert loaded["a"].tolist() == [1, 2]


def test_load_dataset_raises_when_path_is_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        load_dataset(missing)


def test_infer_dataset_name_returns_file_stem() -> None:
    assert (
        infer_dataset_name("data/samples/sample_governance_dataset.csv")
        == "sample_governance_dataset"
    )
