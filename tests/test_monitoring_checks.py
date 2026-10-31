from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.monitoring_components import checks


def test_build_result_preserves_pass_fail_mapping_and_model_fields() -> None:
    passed = checks.build_result("check", True, 1, 2, "high", "details")
    failed = checks.build_result("check", False, 3, 2, "low", "broken")

    assert passed.__dict__ == {
        "check_name": "check",
        "status": "PASS",
        "metric_value": 1,
        "threshold": 2,
        "severity": "high",
        "details": "details",
    }
    assert failed.status == "FAIL"


def test_freshness_preserves_threshold_and_status(tmp_path: Path) -> None:
    path = tmp_path / "published.parquet"
    path.write_bytes(b"data")

    passing = checks.check_file_freshness(path, max_freshness_hours=36)
    failing = checks.check_file_freshness(path, max_freshness_hours=-1)

    assert passing.check_name == "published_file_freshness_hours"
    assert passing.status == "PASS"
    assert passing.threshold == 36
    assert passing.severity == "high"
    assert passing.details.startswith("Ultima modificacao UTC: ")
    assert failing.status == "FAIL"


def test_schema_duplicate_and_volume_checks_preserve_rules() -> None:
    frame = pd.DataFrame(
        {"order_id": ["a", "a"], "order_item_id": [1, 1], "value": [1, 2]}
    )

    schema = checks.check_expected_schema(
        frame, expected_columns={"order_id", "order_item_id", "missing"}
    )
    duplicates = checks.check_primary_key_duplicates(frame)
    passing_volume = checks.check_row_volume(frame, min_rows=2)
    failing_volume = checks.check_row_volume(frame, min_rows=3)

    assert (schema.status, schema.metric_value, schema.threshold) == ("FAIL", 1, 0)
    assert schema.details == "Colunas ausentes: ['missing']"
    assert (duplicates.status, duplicates.metric_value) == ("FAIL", 2)
    assert passing_volume.status == "PASS"
    assert failing_volume.status == "FAIL"
    assert failing_volume.threshold == 3


def test_six_critical_null_checks_keep_order_and_missing_column_behavior() -> None:
    columns = ["a", "b", "c", "d", "e", "f"]
    frame = pd.DataFrame({"a": [1], "b": [None], "c": [1], "d": [1], "e": [1]})

    results = checks.check_critical_nulls(frame, critical_columns=columns)

    assert [result.check_name for result in results] == [
        f"published_critical_nulls__{column}" for column in columns
    ]
    assert len(results) == 6
    assert results[0].status == "PASS"
    assert (results[1].status, results[1].metric_value) == ("FAIL", 1)
    assert (results[-1].status, results[-1].metric_value) == (
        "FAIL",
        "missing_column",
    )


def test_semantic_coverage_preserves_zero_and_one_percent_boundaries() -> None:
    frame = pd.DataFrame(
        {
            "purchase_cohort_month": ["2018-01"] * 100,
            "seller_delay_rate": [0.1] * 99 + [None],
        }
    )

    results = checks.check_semantic_coverage(
        frame, max_missing_seller_delay_rate_pct=1.0
    )

    assert [result.check_name for result in results] == [
        "published_missing_pct__purchase_cohort_month",
        "published_missing_pct__seller_delay_rate",
    ]
    assert [result.status for result in results] == ["PASS", "PASS"]
    assert [result.metric_value for result in results] == [0.0, 1.0]
    assert [result.threshold for result in results] == [0, 1.0]
