from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from src.data_quality import (
    generate_data_quality_table,
    run_data_quality_checks,
)

RESULT_KEYS = [
    "total_rows",
    "total_columns",
    "null_pct_by_column",
    "columns_over_30pct_null",
    "duplicate_rows",
    "dtypes",
    "cardinality",
    "possible_unique_keys",
    "constant_columns",
    "checks",
    "failed_checks_count",
]
CHECK_KEYS = [
    "check_name",
    "status",
    "severity",
    "affected_columns",
    "affected_rows",
    "recommendation",
    "rule_source",
]


def test_generic_profile_and_builtin_heuristics_are_characterized(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    tomorrow = pd.Timestamp(datetime.now(timezone.utc) + timedelta(days=1)).tz_localize(
        None
    )
    yesterday = tomorrow - timedelta(days=2)
    df = pd.DataFrame(
        {
            "id": [1, 2, 2],
            "price": [10.0, -1.0, -1.0],
            "event_date": [yesterday, tomorrow, tomorrow],
            "nullable": ["a", None, None],
            "constant": ["x", "x", "x"],
        }
    )

    result = run_data_quality_checks(df)
    checks = {check["check_name"]: check for check in result["checks"]}

    assert list(result) == RESULT_KEYS
    assert result["total_rows"] == 3
    assert result["total_columns"] == 5
    assert result["null_pct_by_column"] == {
        "nullable": 66.67,
        "id": 0.0,
        "price": 0.0,
        "event_date": 0.0,
        "constant": 0.0,
    }
    assert result["columns_over_30pct_null"] == ["nullable"]
    assert result["duplicate_rows"] == 1
    assert result["cardinality"] == {
        "id": 2,
        "price": 2,
        "event_date": 2,
        "nullable": 2,
        "constant": 1,
    }
    assert result["possible_unique_keys"] == []
    assert result["constant_columns"] == ["constant"]
    assert result["dtypes"] == {
        "id": "int64",
        "price": "float64",
        "event_date": "datetime64[ns]",
        "nullable": "object",
        "constant": "object",
    }
    assert checks["negative_values__price"]["affected_rows"] == 2
    assert checks["future_dates__event_date"]["affected_rows"] == 2
    assert all(list(check) == CHECK_KEYS for check in result["checks"])


def test_empty_dataframe_and_mixed_object_types_preserve_current_behavior(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    empty = run_data_quality_checks(pd.DataFrame())
    mixed = run_data_quality_checks(pd.DataFrame({"mixed": [1, "1", None]}))

    assert empty == {
        "total_rows": 0,
        "total_columns": 0,
        "null_pct_by_column": {},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [
            {
                "check_name": "high_null_columns_over_30pct",
                "status": "PASS",
                "severity": "low",
                "affected_columns": "",
                "affected_rows": 0,
                "recommendation": "Review source completeness and enforce mandatory fields for critical columns.",
                "rule_source": "built_in",
            },
            {
                "check_name": "duplicate_rows",
                "status": "PASS",
                "severity": "low",
                "affected_columns": "",
                "affected_rows": 0,
                "recommendation": "Remove duplicates and validate ingestion keys/grain assumptions.",
                "rule_source": "built_in",
            },
            {
                "check_name": "constant_columns",
                "status": "PASS",
                "severity": "low",
                "affected_columns": "",
                "affected_rows": 0,
                "recommendation": "Drop or review constant columns to simplify the analytical model.",
                "rule_source": "built_in",
            },
        ],
        "failed_checks_count": 0,
    }
    assert mixed["dtypes"] == {"mixed": "object"}
    assert mixed["cardinality"] == {"mixed": 3}
    assert mixed["possible_unique_keys"] == ["mixed"]
    assert mixed["columns_over_30pct_null"] == ["mixed"]


def test_generated_table_preserves_check_column_order(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    table = generate_data_quality_table(pd.DataFrame({"constant": [1, 1]}))

    assert table.columns.tolist() == CHECK_KEYS
    assert table["check_name"].tolist() == [
        "high_null_columns_over_30pct",
        "duplicate_rows",
        "constant_columns",
    ]
    assert table["status"].tolist() == ["PASS", "FAIL", "FAIL"]
