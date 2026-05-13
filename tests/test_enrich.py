from __future__ import annotations

import datetime

import pandas as pd

from src.enrich import add_reference_date


def test_add_reference_date_adds_column_with_today() -> None:
    df = pd.DataFrame({"val": [1, 2, 3]})
    result = add_reference_date(df)

    assert "reference_date" in result.columns
    assert len(result) == 3
    assert isinstance(result["reference_date"].iloc[0], datetime.date)


def test_add_reference_date_does_not_mutate_input() -> None:
    df = pd.DataFrame({"val": [1]})
    add_reference_date(df)

    assert "reference_date" not in df.columns


def test_add_reference_date_respects_custom_column_name() -> None:
    df = pd.DataFrame({"val": [1]})
    result = add_reference_date(df, column_name="snapshot_date")

    assert "snapshot_date" in result.columns
    assert "reference_date" not in result.columns
