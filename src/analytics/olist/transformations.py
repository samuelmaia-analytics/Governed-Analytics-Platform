"""Derived metrics and final column shaping for the Olist analytical mart."""

from __future__ import annotations

import pandas as pd

from src.analytics.olist.cleaning import deduplicate


def derive_columns(fact_table: pd.DataFrame) -> pd.DataFrame:
    enriched = fact_table.copy()

    enriched["order_date"] = enriched["order_purchase_timestamp"].dt.date
    enriched["order_year"] = enriched["order_purchase_timestamp"].dt.year
    enriched["order_month"] = enriched["order_purchase_timestamp"].dt.month
    enriched["purchase_cohort_month"] = (
        enriched["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )
    enriched["delivery_time_days"] = (
        enriched["order_delivered_customer_date"] - enriched["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    enriched["estimated_delay_days"] = (
        enriched["order_delivered_customer_date"]
        - enriched["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400
    enriched["is_delayed"] = (
        enriched["order_delivered_customer_date"].notna()
        & enriched["order_estimated_delivery_date"].notna()
        & (
            enriched["order_delivered_customer_date"]
            > enriched["order_estimated_delivery_date"]
        )
    )
    enriched["total_item_value"] = enriched["price"].fillna(0) + enriched[
        "freight_value"
    ].fillna(0)
    enriched["freight_to_price_ratio"] = (
        enriched["freight_value"]
        .where(enriched["price"].fillna(0) > 0)
        .div(enriched["price"].where(enriched["price"].fillna(0) > 0))
    )
    enriched["seller_dispatch_time_days"] = (
        enriched["order_delivered_carrier_date"] - enriched["order_approved_at"]
    ).dt.total_seconds() / 86400
    enriched["carrier_delivery_time_days"] = (
        enriched["order_delivered_customer_date"]
        - enriched["order_delivered_carrier_date"]
    ).dt.total_seconds() / 86400

    first_purchase_ts = enriched.groupby("customer_unique_id")[
        "order_purchase_timestamp"
    ].transform("min")
    enriched["customer_first_purchase_timestamp"] = first_purchase_ts
    enriched["cohort_order_month_number"] = (
        enriched["order_purchase_timestamp"].dt.year - first_purchase_ts.dt.year
    ) * 12 + (
        enriched["order_purchase_timestamp"].dt.month - first_purchase_ts.dt.month
    )
    order_rank = (
        enriched.groupby(["customer_unique_id", "order_id"], dropna=False)[
            "order_purchase_timestamp"
        ]
        .transform("min")
        .groupby(enriched["customer_unique_id"], dropna=False)
        .rank(method="dense")
    )
    enriched["customer_order_sequence"] = order_rank.astype("Int64")
    enriched["is_first_order"] = enriched["customer_order_sequence"] == 1

    seller_order_count = enriched.groupby("seller_id")["order_id"].transform("nunique")
    enriched["seller_order_count"] = seller_order_count.astype("Int64")
    enriched["seller_avg_delivery_days"] = enriched.groupby("seller_id")[
        "delivery_time_days"
    ].transform("mean")
    enriched["seller_delay_rate"] = enriched.groupby("seller_id")[
        "is_delayed"
    ].transform("mean")
    enriched["seller_volume_tier"] = pd.cut(
        seller_order_count,
        bins=[-1, 25, 100, 500, float("inf")],
        labels=["long_tail", "scaled", "core", "strategic"],
    ).astype("string")

    return enriched


def remove_obvious_inconsistencies(fact_table: pd.DataFrame) -> pd.DataFrame:
    cleaned = fact_table.copy()
    cleaned = cleaned[cleaned["order_purchase_timestamp"].notna()].copy()
    cleaned = cleaned[cleaned["price"].fillna(0) >= 0].copy()
    cleaned = cleaned[cleaned["freight_value"].fillna(0) >= 0].copy()
    cleaned = cleaned[
        cleaned["delivery_time_days"].isna() | (cleaned["delivery_time_days"] >= 0)
    ].copy()
    cleaned = deduplicate(
        cleaned, subset=["order_id", "order_item_id", "product_id", "seller_id"]
    )
    return cleaned


def select_output_columns(fact_table: pd.DataFrame) -> pd.DataFrame:
    preferred_order = [
        "order_id",
        "order_item_id",
        "customer_id",
        "customer_unique_id",
        "product_id",
        "seller_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "shipping_limit_date",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "order_date",
        "order_year",
        "order_month",
        "purchase_cohort_month",
        "customer_first_purchase_timestamp",
        "cohort_order_month_number",
        "customer_order_sequence",
        "is_first_order",
        "delivery_time_days",
        "seller_dispatch_time_days",
        "carrier_delivery_time_days",
        "estimated_delay_days",
        "is_delayed",
        "price",
        "freight_value",
        "freight_to_price_ratio",
        "total_item_value",
        "payment_count",
        "total_payment_value",
        "max_payment_installments",
        "payment_type_mode",
        "review_count",
        "review_score_mean",
        "review_score_max",
        "review_score_min",
        "has_review_comment",
        "product_category_name",
        "product_category_name_english",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
        "seller_order_count",
        "seller_avg_delivery_days",
        "seller_delay_rate",
        "seller_volume_tier",
        "latest_review_creation_date",
        "latest_review_answer_timestamp",
    ]
    existing = [column for column in preferred_order if column in fact_table.columns]
    remaining = [column for column in fact_table.columns if column not in existing]
    return fact_table[existing + remaining].copy()
