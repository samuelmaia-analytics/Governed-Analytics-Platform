from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.monitoring_components.models import MonitoringCheckResult
from src.monitoring_components.pipeline import run_monitoring


def _result(name: str) -> MonitoringCheckResult:
    return MonitoringCheckResult(name, "PASS", 0, 0, "high", name)


def test_pipeline_preserves_check_order_and_dataframe_identity() -> None:
    calls: list[str] = []
    frame = pd.DataFrame({"a": [1]})

    def single(name: str):
        def check(value: pd.DataFrame) -> MonitoringCheckResult:
            calls.append(name)
            assert value is frame
            return _result(name)

        return check

    def multiple(name: str):
        def check(value: pd.DataFrame) -> list[MonitoringCheckResult]:
            calls.append(name)
            assert value is frame
            return [_result(f"{name}-1"), _result(f"{name}-2")]

        return check

    def freshness(path: Path, *, max_freshness_hours: int):
        calls.append("freshness")
        assert path == Path("published.parquet")
        assert max_freshness_hours == 36
        return _result("freshness")

    results = run_monitoring(
        max_freshness_hours=36,
        published_path=Path("published.parquet"),
        load_published_table_fn=lambda: calls.append("load") or frame,
        check_file_freshness_fn=freshness,
        check_expected_schema_fn=single("schema"),
        check_primary_key_duplicates_fn=single("duplicates"),
        check_row_volume_fn=single("volume"),
        check_critical_nulls_fn=multiple("nulls"),
        check_semantic_coverage_fn=multiple("semantic"),
    )

    assert calls == [
        "load",
        "freshness",
        "schema",
        "duplicates",
        "volume",
        "nulls",
        "semantic",
    ]
    assert [result.check_name for result in results] == [
        "freshness",
        "schema",
        "duplicates",
        "volume",
        "nulls-1",
        "nulls-2",
        "semantic-1",
        "semantic-2",
    ]


@pytest.mark.parametrize("step", ["load", "freshness", "schema"])
def test_pipeline_propagates_dependency_errors(step: str) -> None:
    frame = pd.DataFrame({"a": [1]})

    def fail(*args: object, **kwargs: object):
        raise LookupError(step)

    def passing(name: str):
        return lambda *args, **kwargs: _result(name)

    kwargs = {
        "max_freshness_hours": 36,
        "published_path": Path("published.parquet"),
        "load_published_table_fn": lambda: frame,
        "check_file_freshness_fn": passing("freshness"),
        "check_expected_schema_fn": passing("schema"),
        "check_primary_key_duplicates_fn": passing("duplicates"),
        "check_row_volume_fn": passing("volume"),
        "check_critical_nulls_fn": lambda value: [],
        "check_semantic_coverage_fn": lambda value: [],
    }
    key = {
        "load": "load_published_table_fn",
        "freshness": "check_file_freshness_fn",
        "schema": "check_expected_schema_fn",
    }[step]
    kwargs[key] = fail

    with pytest.raises(LookupError, match=step):
        run_monitoring(**kwargs)  # type: ignore[arg-type]
