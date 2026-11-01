from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.quality as quality


def test_load_fact_table_uses_facade_path_and_returns_reader_object(
    tmp_path: Path, monkeypatch
) -> None:
    fact_path = tmp_path / "fact.parquet"
    fact_path.touch()
    expected = pd.DataFrame({"order_id": ["one"]})
    received_paths: list[Path] = []

    def fake_read_parquet(path: Path) -> pd.DataFrame:
        received_paths.append(path)
        return expected

    monkeypatch.setattr(quality, "FACT_TABLE_PATH", fact_path)
    monkeypatch.setattr(quality.pd, "read_parquet", fake_read_parquet)

    actual = quality.load_fact_table()

    assert received_paths == [fact_path]
    assert actual is expected


def test_load_fact_table_propagates_reader_error(tmp_path: Path, monkeypatch) -> None:
    fact_path = tmp_path / "fact.parquet"
    fact_path.touch()

    def fail_read(_path: Path) -> pd.DataFrame:
        raise OSError("reader failed")

    monkeypatch.setattr(quality, "FACT_TABLE_PATH", fact_path)
    monkeypatch.setattr(quality.pd, "read_parquet", fail_read)

    with pytest.raises(OSError, match="reader failed"):
        quality.load_fact_table()


def test_validate_not_empty_preserves_public_exception_contract() -> None:
    quality.validate_not_empty(pd.DataFrame({"value": [1]}), "orders")

    with pytest.raises(ValueError, match=r"^orders is empty\.$"):
        quality.validate_not_empty(pd.DataFrame(), "orders")


def test_main_preserves_order_and_object_identity(monkeypatch) -> None:
    df = pd.DataFrame({"value": [1]})
    results = [object()]
    events: list[tuple[str, object | None]] = []

    monkeypatch.setattr(quality, "configure_logging", lambda: None)
    monkeypatch.setattr(
        quality, "load_fact_table", lambda: events.append(("load", None)) or df
    )
    monkeypatch.setattr(
        quality,
        "run_quality_checks",
        lambda received: events.append(("checks", received)) or results,
    )
    monkeypatch.setattr(
        quality,
        "save_quality_results",
        lambda received: events.append(("save_results", received)),
    )
    monkeypatch.setattr(
        quality,
        "save_quality_report",
        lambda received_df, received_results: events.append(
            ("save_report", (received_df, received_results))
        ),
    )

    quality.main()

    assert [event[0] for event in events] == [
        "load",
        "checks",
        "save_results",
        "save_report",
    ]
    assert events[1][1] is df
    assert events[2][1] is results
    report_df, report_results = events[3][1]
    assert report_df is df
    assert report_results is results


@pytest.mark.parametrize(
    ("failing_step", "expected_events"),
    [
        ("load", ["load"]),
        ("checks", ["load", "checks"]),
        ("save_results", ["load", "checks", "save_results"]),
        ("save_report", ["load", "checks", "save_results", "save_report"]),
    ],
)
def test_main_propagates_errors_and_stops_subsequent_steps(
    failing_step: str, expected_events: list[str], monkeypatch
) -> None:
    df = pd.DataFrame({"value": [1]})
    results = [object()]
    events: list[str] = []

    def step(name: str, returned):
        events.append(name)
        if name == failing_step:
            raise RuntimeError(f"{name} failed")
        return returned

    monkeypatch.setattr(quality, "configure_logging", lambda: None)
    monkeypatch.setattr(quality, "load_fact_table", lambda: step("load", df))
    monkeypatch.setattr(
        quality, "run_quality_checks", lambda _df: step("checks", results)
    )
    monkeypatch.setattr(
        quality, "save_quality_results", lambda _results: step("save_results", None)
    )
    monkeypatch.setattr(
        quality,
        "save_quality_report",
        lambda _df, _results: step("save_report", None),
    )

    with pytest.raises(RuntimeError, match=f"^{failing_step} failed$"):
        quality.main()

    assert events == expected_events
