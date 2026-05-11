from __future__ import annotations

import pandas as pd

from src.export_power_bi import build_export_bundle, validate_export_bundle


def build_source_df() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "order_id": ["o1", "o2"],
            "order_item_id": [1, 1],
            "order_date": [pd.Timestamp("2018-01-01"), pd.Timestamp("2018-01-02")],
            "customer_id": ["c1", "c2"],
            "customer_unique_id": ["cu1", "cu2"],
            "customer_state": ["SP", "RJ"],
            "product_id": ["p1", "p2"],
            "product_category_name": ["beleza", "casa"],
            "product_category_name_english": ["beauty", "house"],
            "seller_id": ["s1", "s2"],
            "seller_state": ["MG", "BA"],
            "payment_type_mode": ["credit_card", "boleto"],
            "order_status": ["delivered", "approved"],
            "order_purchase_timestamp": [
                pd.Timestamp("2018-01-01 10:00:00"),
                pd.Timestamp("2018-01-02 11:00:00"),
            ],
            "order_approved_at": [
                pd.Timestamp("2018-01-01 12:00:00"),
                pd.Timestamp("2018-01-02 12:00:00"),
            ],
            "order_delivered_customer_date": [
                pd.Timestamp("2018-01-05 14:00:00"),
                pd.NaT,
            ],
            "order_estimated_delivery_date": [
                pd.Timestamp("2018-01-06"),
                pd.Timestamp("2018-01-07"),
            ],
            "price": [100.0, 200.0],
            "freight_value": [10.0, 20.0],
            "total_item_value": [110.0, 220.0],
            "payment_count": [1, 1],
            "total_payment_value": [110.0, 220.0],
            "max_payment_installments": [2, 1],
            "review_count": [1, 0],
            "review_score_mean": [4.5, pd.NA],
            "delivery_time_days": [4.0, pd.NA],
            "estimated_delay_days": [-1.0, pd.NA],
            "is_delayed": [False, False],
            "product_name_lenght": [10.0, 20.0],
            "product_description_lenght": [100.0, 200.0],
            "product_photos_qty": [1.0, 2.0],
            "product_weight_g": [500.0, 800.0],
            "product_length_cm": [10.0, 20.0],
            "product_height_cm": [5.0, 6.0],
            "product_width_cm": [7.0, 8.0],
        }
    )
    df["category_label"] = (
        df["product_category_name_english"]
        .fillna(df["product_category_name"])
        .fillna("unknown")
    )
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
    assert {
        "date_key",
        "product_key",
        "payment_key",
        "order_status_key",
        "customer_key",
        "seller_key",
    }.issubset(bundle.fact_sales.columns)


def test_validate_export_bundle_accepts_consistent_model() -> None:
    bundle = build_export_bundle(build_source_df())
    validate_export_bundle(bundle)

    assert bundle.dim_date["date_key"].is_unique
    assert bundle.dim_product["product_key"].is_unique
    assert bundle.dim_payment["payment_key"].is_unique
    assert bundle.dim_order_status["order_status_key"].is_unique
    assert bundle.dim_customer["customer_key"].is_unique
    assert bundle.dim_seller["seller_key"].is_unique

    assert (
        bundle.fact_sales["payment_key"].isin(bundle.dim_payment["payment_key"]).all()
    )
    assert (
        bundle.fact_sales["order_status_key"]
        .isin(bundle.dim_order_status["order_status_key"])
        .all()
    )
