from __future__ import annotations

import pandas as pd

from src.export_power_bi import build_export_bundle, validate_export_bundle


def build_source_df() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "order_id": ["o1", "o2"],
            "order_item_id": [1, 1],
            "order_date": [pd.Timestamp("2018-01-01"), pd.Timestamp("2018-01-02")],
            "customer_unique_id": ["customer_unique_id_1", "customer_unique_id_2"],
            "customer_state": ["SP", "RJ"],
            "product_category_name": ["beleza", "casa"],
            "product_category_name_english": ["beauty", "house"],
            "seller_key": ["seller_id_1", "seller_id_2"],
            "seller_state": ["MG", "BA"],
            "payment_type_mode": ["credit_card", "boleto"],
            "order_status": ["delivered", "approved"],
            "order_purchase_timestamp": [pd.Timestamp("2018-01-01 10:00:00"), pd.Timestamp("2018-01-02 11:00:00")],
            "order_delivered_customer_date": [pd.Timestamp("2018-01-05 14:00:00"), pd.NaT],
            "order_estimated_delivery_date": [pd.Timestamp("2018-01-06"), pd.Timestamp("2018-01-07")],
            "price": [100.0, 200.0],
            "freight_value": [10.0, 20.0],
            "total_item_value": [110.0, 220.0],
            "review_score_mean": [4.5, pd.NA],
            "delivery_time_days": [4.0, pd.NA],
            "estimated_delay_days": [-1.0, pd.NA],
            "is_delayed": [False, False],
        }
    )
    df["category_label"] = df["product_category_name_english"].fillna(df["product_category_name"]).fillna("unknown")
    df["payment_type_mode"] = df["payment_type_mode"].fillna("unknown").astype(str)
    df["order_status"] = df["order_status"].fillna("unknown").astype(str)
    df["customer_state"] = df["customer_state"].fillna("NA").astype(str)
    df["seller_state"] = df["seller_state"].fillna("NA").astype(str)
    df["is_delayed"] = df["is_delayed"].fillna(False).astype(bool)
    return df


def test_build_export_bundle_creates_star_schema_with_expected_keys() -> None:
    bundle = build_export_bundle(build_source_df())

    assert list(bundle.dim_date.columns) == [
        "date_key",
        "order_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "year_month",
        "week_of_year",
        "day",
        "weekday_name",
    ]
    assert list(bundle.dim_payment.columns) == [
        "payment_key",
        "payment_type",
        "payment_group",
        "payment_description",
    ]
    assert list(bundle.dim_order_status.columns) == [
        "order_status_key",
        "order_status",
        "status_group",
        "status_description",
    ]
    assert {"date_key", "category_key", "payment_key", "order_status_key", "customer_key", "seller_key"}.issubset(
        bundle.fact_sales.columns
    )


def test_validate_export_bundle_accepts_consistent_model() -> None:
    bundle = build_export_bundle(build_source_df())
    validate_export_bundle(bundle)

    assert bundle.dim_date["date_key"].is_unique
    assert bundle.dim_category["category_key"].is_unique
    assert bundle.dim_payment["payment_key"].is_unique
    assert bundle.dim_order_status["order_status_key"].is_unique
    assert bundle.dim_customer["customer_key"].is_unique
    assert bundle.dim_seller["seller_key"].is_unique

    assert bundle.fact_sales["payment_key"].isin(bundle.dim_payment["payment_key"]).all()
    assert bundle.fact_sales["order_status_key"].isin(bundle.dim_order_status["order_status_key"]).all()
