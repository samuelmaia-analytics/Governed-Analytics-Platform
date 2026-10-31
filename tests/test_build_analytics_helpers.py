from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.build_analytics as build_analytics
from src.duckdb_engine import execute_query


def test_to_snake_case_and_standardize_columns_handle_mixed_input() -> None:
    df = pd.DataFrame({"Order ID": [1], "CustomerID": [2]})

    standardized = build_analytics.standardize_columns(df)

    assert build_analytics.to_snake_case("Order ID") == "order_id"
    assert list(standardized.columns) == ["order_id", "customer_id"]


def test_read_olist_table_prefers_standardized_parquet(
    tmp_path: Path, monkeypatch
) -> None:
    standardized_dir = tmp_path / "standardized"
    standardized_dir.mkdir()
    landing_dir = tmp_path / "landing"
    landing_dir.mkdir()
    source = pd.DataFrame({"Order ID": [1], "OrderDate": ["2018-01-01"]})
    source.to_parquet(standardized_dir / "olist_orders_dataset.parquet", index=False)
    pd.DataFrame({"Order ID": [2]}).to_csv(
        landing_dir / "olist_orders_dataset.csv", index=False
    )

    monkeypatch.setattr(build_analytics, "STANDARDIZED_OLIST_DIR", standardized_dir)
    monkeypatch.setattr(build_analytics, "OLIST_LANDING_DIR", landing_dir)

    result = build_analytics.read_olist_table("olist_orders_dataset.csv")

    assert list(result.columns) == ["order_id", "order_date"]
    assert int(result.loc[0, "order_id"]) == 1


def test_read_olist_table_falls_back_to_landing_csv(
    tmp_path: Path, monkeypatch
) -> None:
    standardized_dir = tmp_path / "standardized"
    landing_dir = tmp_path / "landing"
    standardized_dir.mkdir()
    landing_dir.mkdir()
    pd.DataFrame({"Order ID": [2], "CustomerID": [3]}).to_csv(
        landing_dir / "olist_orders_dataset.csv", index=False
    )

    monkeypatch.setattr(build_analytics, "STANDARDIZED_OLIST_DIR", standardized_dir)
    monkeypatch.setattr(build_analytics, "OLIST_LANDING_DIR", landing_dir)

    result = build_analytics.read_olist_table("olist_orders_dataset.csv")

    assert list(result.columns) == ["order_id", "customer_id"]
    assert int(result.loc[0, "order_id"]) == 2


def test_read_olist_table_raises_when_no_source_exists(
    tmp_path: Path, monkeypatch
) -> None:
    standardized_dir = tmp_path / "standardized"
    landing_dir = tmp_path / "landing"
    monkeypatch.setattr(build_analytics, "STANDARDIZED_OLIST_DIR", standardized_dir)
    monkeypatch.setattr(build_analytics, "OLIST_LANDING_DIR", landing_dir)

    with pytest.raises(FileNotFoundError) as exc_info:
        build_analytics.read_olist_table("olist_orders_dataset.csv")

    expected_standardized = standardized_dir / "olist_orders_dataset.parquet"
    expected_landing = landing_dir / "olist_orders_dataset.csv"
    assert str(exc_info.value) == (
        "Arquivo não encontrado em standardized nem landing: "
        f"{expected_standardized} | {expected_landing}"
    )


def test_convert_datetime_columns_and_deduplicate_work_together() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["o1", "o1"],
            "order_purchase_timestamp": ["2018-01-01 10:00:00", "2018-01-01 10:00:00"],
            "text": ["a", "a"],
        }
    )

    converted = build_analytics.convert_datetime_columns(df)
    deduplicated = build_analytics.deduplicate(converted)

    assert str(converted["order_purchase_timestamp"].dtype).startswith("datetime64")
    assert len(deduplicated) == 1


def test_build_payments_and_reviews_aggregations_return_expected_metrics() -> None:
    payments = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "payment_sequential": [1, 2, 1],
            "payment_value": [100.0, 20.0, 50.0],
            "payment_installments": [2, 4, 1],
            "payment_type": ["credit_card", "credit_card", "boleto"],
        }
    )
    reviews = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "review_id": ["r1", "r2", "r3"],
            "review_score": [4, 5, 3],
            "review_creation_date": pd.to_datetime(
                ["2018-01-02", "2018-01-03", "2018-01-04"]
            ),
            "review_answer_timestamp": pd.to_datetime(
                ["2018-01-05", "2018-01-06", "2018-01-07"]
            ),
            "review_comment_message": ["ok", "", None],
        }
    )

    payments_agg = build_analytics.build_payments_agg(payments)
    reviews_agg = build_analytics.build_reviews_agg(reviews)

    assert (
        float(
            payments_agg.loc[
                payments_agg["order_id"] == "o1", "total_payment_value"
            ].iloc[0]
        )
        == 120.0
    )
    assert (
        int(reviews_agg.loc[reviews_agg["order_id"] == "o1", "review_count"].iloc[0])
        == 2
    )
    assert (
        int(
            reviews_agg.loc[reviews_agg["order_id"] == "o1", "has_review_comment"].iloc[
                0
            ]
        )
        == 1
    )


def test_clean_helpers_filter_missing_keys() -> None:
    orders = pd.DataFrame({"order_id": ["o1", None], "customer_id": ["c1", "c2"]})
    items = pd.DataFrame(
        {
            "order_id": ["o1", "o2"],
            "order_item_id": [1, None],
            "product_id": ["p1", "p2"],
            "seller_id": ["s1", "s2"],
            "price": [10.0, -1.0],
            "freight_value": [1.0, 1.0],
        }
    )

    assert len(build_analytics.clean_orders(orders)) == 1
    assert len(build_analytics.clean_order_items(items)) == 1
    assert (
        len(
            build_analytics.clean_customers(pd.DataFrame({"customer_id": ["c1", None]}))
        )
        == 1
    )
    assert (
        len(build_analytics.clean_products(pd.DataFrame({"product_id": ["p1", None]})))
        == 1
    )
    assert (
        len(build_analytics.clean_sellers(pd.DataFrame({"seller_id": ["s1", None]})))
        == 1
    )
    assert (
        len(
            build_analytics.clean_translation(
                pd.DataFrame({"product_category_name": ["cat", None]})
            )
        )
        == 1
    )


def test_join_health_reconciliation_and_output_order_are_reported() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "order_item_id": [1, 2, 1],
            "product_id": ["p1", "p2", "p3"],
            "seller_id": ["s1", "s1", "s2"],
            "customer_unique_id": ["c1", None, "c2"],
            "customer_state": ["SP", "SP", None],
            "seller_state": ["RJ", "RJ", "MG"],
            "payment_type_mode": ["credit_card", "credit_card", None],
            "product_category_name": ["cat_a", None, "cat_c"],
            "product_category_name_english": ["cat a", "cat b", None],
            "total_item_value": [10.0, 15.0, 20.0],
            "total_payment_value": [25.0, 25.0, 18.0],
            "price": [8.0, 12.0, 18.0],
            "freight_value": [2.0, 3.0, 2.0],
        }
    )

    join_health = build_analytics.build_join_health_summary(df)
    reconciliation = build_analytics.build_payment_reconciliation_summary(df)
    ordered = build_analytics.select_output_columns(df.assign(order_status="delivered"))

    assert join_health["customer_unique_id"] == round(1 / 3 * 100, 2)
    assert reconciliation["orders_reconciled"] == 2
    assert ordered.columns[0] == "order_id"


def test_render_report_save_report_and_run_build_return_artifacts(
    tmp_path: Path, monkeypatch
) -> None:
    fact_df = pd.DataFrame(
        {
            "order_id": ["o1"] * 100_002,
            "order_item_id": [1] * 100_002,
            "customer_id": ["c1"] * 100_002,
            "customer_unique_id": ["cu1"] * 100_002,
            "product_id": ["p1"] * 100_002,
            "seller_id": ["s1"] * 100_002,
            "order_status": ["delivered"] * 100_002,
            "order_purchase_timestamp": pd.to_datetime(["2018-01-01"] * 100_002),
            "order_approved_at": pd.to_datetime(["2018-01-01"] * 100_002),
            "order_delivered_customer_date": pd.to_datetime(["2018-01-03"] * 100_002),
            "order_estimated_delivery_date": pd.to_datetime(["2018-01-02"] * 100_002),
            "order_date": pd.to_datetime(["2018-01-01"] * 100_002),
            "order_year": [2018] * 100_002,
            "order_month": [1] * 100_002,
            "delivery_time_days": [2.0] * 100_002,
            "estimated_delay_days": [1.0] * 100_002,
            "is_delayed": [True] * 100_002,
            "price": [100.0] * 100_002,
            "freight_value": [10.0] * 100_002,
            "total_item_value": [110.0] * 100_002,
            "payment_count": [1] * 100_002,
            "total_payment_value": [110.0] * 100_002,
            "max_payment_installments": [1] * 100_002,
            "payment_type_mode": ["credit_card"] * 100_002,
            "review_count": [1] * 100_002,
            "review_score_mean": [4.5] * 100_002,
            "review_score_max": [5.0] * 100_002,
            "review_score_min": [4.0] * 100_002,
            "has_review_comment": [1] * 100_002,
            "product_category_name": ["cat_a"] * 100_002,
            "product_category_name_english": ["cat a"] * 100_002,
            "customer_state": ["SP"] * 100_002,
            "seller_state": ["RJ"] * 100_002,
        }
    )
    analytics_dir = tmp_path / "analytics"
    docs_dir = tmp_path / "docs"

    monkeypatch.setattr(build_analytics, "ANALYTICS_DIR", analytics_dir)
    monkeypatch.setattr(build_analytics, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(
        build_analytics,
        "FACT_PARQUET_PATH",
        analytics_dir / "fact_orders_enriched.parquet",
    )
    monkeypatch.setattr(
        build_analytics, "FACT_CSV_PATH", analytics_dir / "fact_orders_enriched.csv"
    )
    monkeypatch.setattr(
        build_analytics, "FACT_DUCKDB_PATH", analytics_dir / "governance.duckdb"
    )
    monkeypatch.setattr(
        build_analytics, "REPORT_PATH", docs_dir / "fact_orders_enriched.md"
    )
    monkeypatch.setattr(build_analytics, "build_fact_orders_enriched", lambda: fact_df)

    report = build_analytics.render_report(fact_df)
    artifacts = build_analytics.run_build()

    assert "fact_orders_enriched" in report
    assert artifacts.parquet_path.exists()
    assert artifacts.csv_path.exists()
    assert artifacts.duckdb_path.exists()
    assert artifacts.report_path.exists()
    persisted = execute_query(
        "SELECT COUNT(*) AS total_rows FROM fact_orders_enriched",
        db_path=artifacts.duckdb_path,
    )
    assert int(persisted.loc[0, "total_rows"]) == len(fact_df)


def test_run_build_respects_facade_monkeypatches(
    tmp_path: Path, monkeypatch
) -> None:
    fact_df = pd.DataFrame({"order_id": ["o1"]})
    parquet_path = tmp_path / "fact.parquet"
    csv_path = tmp_path / "fact.csv"
    duckdb_path = tmp_path / "fact.duckdb"
    report_path = tmp_path / "fact.md"
    call_order: list[str] = []

    def fake_build_fact() -> pd.DataFrame:
        call_order.append("build")
        return fact_df

    def fake_save_outputs(df: pd.DataFrame) -> tuple[Path, Path, Path]:
        call_order.append("outputs")
        assert df is fact_df
        return parquet_path, csv_path, duckdb_path

    def fake_save_report(df: pd.DataFrame) -> Path:
        call_order.append("report")
        assert df is fact_df
        return report_path

    monkeypatch.setattr(build_analytics, "build_fact_orders_enriched", fake_build_fact)
    monkeypatch.setattr(build_analytics, "save_outputs", fake_save_outputs)
    monkeypatch.setattr(build_analytics, "save_report", fake_save_report)

    artifacts = build_analytics.run_build()

    assert call_order == ["build", "outputs", "report"]
    assert artifacts.fact_table is fact_df
    assert artifacts.parquet_path == parquet_path
    assert artifacts.csv_path == csv_path
    assert artifacts.duckdb_path == duckdb_path
    assert artifacts.report_path == report_path
