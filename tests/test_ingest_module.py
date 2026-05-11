from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.ingest as ingest


def test_detect_date_columns_identifies_date_and_timestamp_fields(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sample.csv"
    path.write_text(
        "event_date,created_timestamp,name\n2024-01-01,2024-01-01 10:00:00,a\n",
        encoding="utf-8",
    )

    result = ingest.detect_date_columns(path)

    assert result == ["event_date", "created_timestamp"]


def test_load_csv_falls_back_to_plain_read_when_parse_dates_fails(
    monkeypatch, tmp_path: Path
) -> None:
    path = tmp_path / "sample.csv"
    path.write_text("event_date,name\nnot-a-date,a\n", encoding="utf-8")

    calls: list[tuple[str, tuple[str, ...] | None]] = []
    original_read_csv = pd.read_csv

    def fake_read_csv(*args, **kwargs):  # type: ignore[no-untyped-def]
        parse_dates = kwargs.get("parse_dates")
        calls.append(
            (
                kwargs.get("encoding", "utf-8"),
                tuple(parse_dates) if parse_dates else None,
            )
        )
        if parse_dates:
            raise ValueError("bad parse")
        return original_read_csv(*args, **kwargs)

    monkeypatch.setattr(ingest.pd, "read_csv", fake_read_csv)

    df, encoding, parsed_dates = ingest.load_csv(path)

    assert list(df.columns) == ["event_date", "name"]
    assert encoding == "utf-8"
    assert parsed_dates == []
    assert ("utf-8", ("event_date",)) in calls
    assert ("utf-8", None) in calls


def test_validate_expected_files_returns_all_csvs_when_dataset_is_complete(
    tmp_path: Path, monkeypatch
) -> None:
    raw_dir = tmp_path / "olist"
    raw_dir.mkdir()
    for file_name in ingest.EXPECTED_FILES:
        (raw_dir / file_name).write_text("id\n1\n", encoding="utf-8")

    monkeypatch.setattr(ingest, "OLIST_RAW_DIR", raw_dir)

    discovered = ingest.validate_expected_files()

    assert [path.name for path in discovered] == sorted(ingest.EXPECTED_FILES)


def test_validate_expected_files_raises_when_any_expected_file_is_missing(
    tmp_path: Path, monkeypatch
) -> None:
    raw_dir = tmp_path / "olist"
    raw_dir.mkdir()
    for file_name in ingest.EXPECTED_FILES[:-1]:
        (raw_dir / file_name).write_text("id\n1\n", encoding="utf-8")

    monkeypatch.setattr(ingest, "OLIST_RAW_DIR", raw_dir)

    with pytest.raises(FileNotFoundError):
        ingest.validate_expected_files()


def test_render_inventory_markdown_includes_dataset_metadata() -> None:
    markdown = ingest.render_inventory_markdown(
        [
            ingest.DatasetSummary(
                file_name="sample.csv",
                relative_path="data/raw/landing/olist/sample.csv",
                rows=10,
                columns_count=2,
                columns=["order_id", "order_date"],
                dtypes={"order_id": "object", "order_date": "datetime64[ns]"},
                parsed_date_columns=["order_date"],
                encoding="utf-8",
            )
        ]
    )

    assert "Inventário de Dados Brutos" in markdown
    assert "`sample.csv`" not in markdown
    assert "data/raw/landing/olist/sample.csv" in markdown
    assert "| `order_date` | `datetime64[ns]` |" in markdown


def test_save_inventory_persists_rendered_markdown(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "raw_data_inventory.md"
    monkeypatch.setattr(ingest, "INVENTORY_PATH", target)
    monkeypatch.setattr(ingest, "DOCS_DIR", tmp_path)

    result = ingest.save_inventory(
        [
            ingest.DatasetSummary(
                file_name="sample.csv",
                relative_path="data/raw/landing/olist/sample.csv",
                rows=1,
                columns_count=1,
                columns=["id"],
                dtypes={"id": "int64"},
                parsed_date_columns=[],
                encoding="utf-8",
            )
        ]
    )

    assert result == target
    assert target.exists()
    assert "sample.csv" in target.read_text(encoding="utf-8")
