from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.scorecard_components.readers import read_csv


def test_missing_evidence_returns_empty_dataframe(tmp_path: Path) -> None:
    result = read_csv(tmp_path / "missing.csv")
    assert result.empty
    assert result.columns.empty


def test_reader_preserves_columns_status_and_severity(tmp_path: Path) -> None:
    path = tmp_path / "evidence.csv"
    expected = pd.DataFrame({"status": ["WARN"], "severity": ["unknown"]})
    expected.to_csv(path, index=False)
    pd.testing.assert_frame_equal(read_csv(path), expected)


def test_physically_empty_csv_keeps_pandas_exception(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(pd.errors.EmptyDataError):
        read_csv(path)
