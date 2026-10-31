from __future__ import annotations

import json
from dataclasses import asdict, fields
from pathlib import Path

import pandas as pd

import src.published_monitoring as monitoring

EXPECTED_CHECKS = [
    "published_file_freshness_hours",
    "published_expected_schema",
    "published_primary_key_duplicates",
    "published_min_rows",
    "published_critical_nulls__order_id",
    "published_critical_nulls__order_item_id",
    "published_critical_nulls__seller_key",
    "published_critical_nulls__order_purchase_timestamp",
    "published_critical_nulls__price",
    "published_critical_nulls__freight_value",
    "published_missing_pct__purchase_cohort_month",
    "published_missing_pct__seller_delay_rate",
]


def _passing_frame() -> pd.DataFrame:
    rows = monitoring.MIN_ROWS
    data = {column: [1] * rows for column in monitoring.EXPECTED_COLUMNS}
    data.update(
        {
            "order_id": range(rows),
            "order_item_id": [1] * rows,
            "purchase_cohort_month": ["2018-01"] * rows,
            "seller_delay_rate": [0.0] * rows,
        }
    )
    return pd.DataFrame(data)


def test_monitoring_check_model_and_golden_artifact_are_stable() -> None:
    artifact = pd.read_csv(monitoring.RESULTS_PATH)

    assert [field.name for field in fields(monitoring.MonitoringCheckResult)] == [
        "check_name",
        "status",
        "metric_value",
        "threshold",
        "severity",
        "details",
    ]
    assert artifact["check_name"].tolist() == EXPECTED_CHECKS
    assert artifact.shape == (12, 6)
    assert artifact["status"].value_counts().to_dict() == {"PASS": 12}
    assert artifact["threshold"].tolist() == [
        36.0,
        0.0,
        0.0,
        100001.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    ]


def test_run_monitoring_preserves_order_thresholds_and_messages(
    tmp_path: Path, monkeypatch
) -> None:
    published_path = tmp_path / "published.parquet"
    published_path.write_bytes(b"characterization")
    monkeypatch.setattr(monitoring, "PUBLISHED_PARQUET_PATH", published_path)
    monkeypatch.setattr(monitoring, "load_published_table", lambda: _passing_frame())

    results = monitoring.run_monitoring()

    assert [result.check_name for result in results] == EXPECTED_CHECKS
    assert all(result.status == "PASS" for result in results)
    assert [result.threshold for result in results] == [
        36,
        0,
        0,
        100_001,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1.0,
    ]
    assert results[2].details == (
        "Duplicidades na granularidade publicada `order_id + order_item_id`."
    )
    assert results[-2].details == "Cobertura da semantica de cohort."
    assert results[-1].details == "Cobertura da semantica de seller."


def test_monitoring_writers_preserve_serialized_structure_in_tmp_path(
    tmp_path: Path, monkeypatch
) -> None:
    output_dir = tmp_path / "monitoring"
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(monitoring, "PUBLISHED_MONITORING_DIR", output_dir)
    monkeypatch.setattr(monitoring, "RESULTS_PATH", output_dir / "results.csv")
    monkeypatch.setattr(monitoring, "SUMMARY_PATH", output_dir / "summary.json")
    monkeypatch.setattr(monitoring, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(monitoring, "REPORT_PATH", docs_dir / "monitoring.md")
    results = [
        monitoring.MonitoringCheckResult(
            "published_file_freshness_hours", "PASS", 1.0, 36, "high", "fresh"
        )
    ]

    csv_path, json_path = monitoring.save_results(results)
    report_path = monitoring.save_report(results)
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert pd.read_csv(csv_path).columns.tolist() == list(asdict(results[0]))
    assert payload["total_checks"] == 1
    assert payload["failed_checks"] == 0
    assert payload["results"] == [asdict(results[0])]
    assert "Checks aprovados: **1**" in report_path.read_text(encoding="utf-8")
