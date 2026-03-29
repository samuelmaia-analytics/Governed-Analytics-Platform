from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.published_monitoring as monitoring


def build_published_df() -> pd.DataFrame:
    row_count = 100_001
    return pd.DataFrame(
        {
            "order_id": [f"o{idx}" for idx in range(row_count)],
            "order_item_id": [1] * row_count,
            "customer_unique_id": [f"c{idx}" for idx in range(row_count)],
            "order_purchase_timestamp": pd.to_datetime(["2018-01-01"] * row_count),
            "purchase_cohort_month": ["2018-01"] * row_count,
            "customer_order_sequence": [1] * row_count,
            "is_first_order": [True] * row_count,
            "seller_key": ["s1"] * row_count,
            "seller_volume_tier": ["core"] * row_count,
            "seller_delay_rate": [0.1] * row_count,
            "delivery_time_days": [3.0] * row_count,
            "seller_dispatch_time_days": [1.0] * row_count,
            "carrier_delivery_time_days": [2.0] * row_count,
            "estimated_delay_days": [0.0] * row_count,
            "is_delayed": [False] * row_count,
            "price": [100.0] * row_count,
            "freight_value": [10.0] * row_count,
            "freight_to_price_ratio": [0.1] * row_count,
            "total_item_value": [110.0] * row_count,
        }
    )


def test_run_monitoring_and_save_outputs(tmp_path: Path, monkeypatch) -> None:
    parquet_path = tmp_path / "fact_orders_dashboard.parquet"
    monitoring_dir = tmp_path / "monitoring"
    docs_dir = tmp_path / "docs"
    build_published_df().to_parquet(parquet_path, index=False)

    monkeypatch.setattr(monitoring, "PUBLISHED_PARQUET_PATH", parquet_path)
    monkeypatch.setattr(monitoring, "PUBLISHED_MONITORING_DIR", monitoring_dir)
    monkeypatch.setattr(monitoring, "RESULTS_PATH", monitoring_dir / "published_layer_monitoring.csv")
    monkeypatch.setattr(monitoring, "SUMMARY_PATH", monitoring_dir / "published_layer_monitoring.json")
    monkeypatch.setattr(monitoring, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(monitoring, "REPORT_PATH", docs_dir / "published_layer_monitoring.md")

    results = monitoring.run_monitoring(max_freshness_hours=999)
    monitoring.save_results(results)
    monitoring.save_report(results)

    assert all(result.status == "PASS" for result in results)
    assert (monitoring_dir / "published_layer_monitoring.csv").exists()
    assert (monitoring_dir / "published_layer_monitoring.json").exists()
    assert (docs_dir / "published_layer_monitoring.md").exists()


def test_run_monitoring_returns_failed_checks_when_schema_is_incomplete(tmp_path: Path, monkeypatch) -> None:
    parquet_path = tmp_path / "fact_orders_dashboard.parquet"
    incomplete_df = build_published_df().drop(columns=["seller_delay_rate", "order_purchase_timestamp"])
    incomplete_df.to_parquet(parquet_path, index=False)

    monkeypatch.setattr(monitoring, "PUBLISHED_PARQUET_PATH", parquet_path)

    results = monitoring.run_monitoring(max_freshness_hours=999)

    by_check = {result.check_name: result for result in results}
    assert by_check["published_expected_schema"].status == "FAIL"
    assert by_check["published_critical_nulls__order_purchase_timestamp"].status == "FAIL"
    assert by_check["published_critical_nulls__order_purchase_timestamp"].metric_value == "missing_column"
    assert by_check["published_semantic_coverage_schema"].status == "FAIL"
