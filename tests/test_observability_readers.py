from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.observability_components import readers


def test_missing_history_returns_empty_dataframe(tmp_path: Path) -> None:
    result = readers.load_governance_history(tmp_path / "missing.csv")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert result.columns.empty


def test_history_is_sorted_by_execution_timestamp_without_parsing(
    tmp_path: Path,
) -> None:
    path = tmp_path / "history.csv"
    pd.DataFrame(
        {
            "execution_timestamp": ["2026-01-02T00:00:00Z", "2026-01-01T00:00:00Z"],
            "row_count": [2, 1],
        }
    ).to_csv(path, index=False)

    result = readers.load_governance_history(path)

    assert result["row_count"].tolist() == [1, 2]
    assert result["execution_timestamp"].dtype == object


def test_history_without_timestamp_preserves_row_order(tmp_path: Path) -> None:
    path = tmp_path / "history.csv"
    pd.DataFrame({"row_count": [2, 1]}).to_csv(path, index=False)

    result = readers.load_governance_history(path)

    assert result["row_count"].tolist() == [2, 1]


def test_empty_csv_error_is_propagated(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(pd.errors.EmptyDataError):
        readers.load_governance_history(path)


def test_reader_error_is_propagated_with_expected_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "invalid.csv"
    path.write_text("invalid", encoding="utf-8")

    def fail(actual_path: Path) -> pd.DataFrame:
        assert actual_path == path
        raise ValueError("invalid history")

    monkeypatch.setattr(readers.pd, "read_csv", fail)

    with pytest.raises(ValueError, match="invalid history"):
        readers.load_governance_history(path)

