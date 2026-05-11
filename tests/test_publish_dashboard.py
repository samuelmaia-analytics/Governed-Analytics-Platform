from __future__ import annotations

import pandas as pd

from src.publish_dashboard import build_published_dashboard_table


def test_build_published_dashboard_table_minimizes_sensitive_columns_and_pseudonymizes_keys() -> (
    None
):
    source_df = pd.DataFrame(
        {
            "order_id": ["order-1"],
            "order_item_id": [1],
            "customer_id": ["cust-trans-1"],
            "customer_unique_id": ["cust-uniq-1"],
            "product_id": ["product-1"],
            "seller_id": ["seller-1"],
            "order_status": ["delivered"],
            "order_purchase_timestamp": [pd.Timestamp("2018-01-01 10:00:00")],
            "order_delivered_customer_date": [pd.Timestamp("2018-01-05 13:00:00")],
            "order_estimated_delivery_date": [pd.Timestamp("2018-01-04")],
            "order_date": [pd.Timestamp("2018-01-01").date()],
            "order_year": [2018],
            "order_month": [1],
            "purchase_cohort_month": ["2018-01"],
            "cohort_order_month_number": [0],
            "customer_order_sequence": [1],
            "is_first_order": [True],
            "seller_volume_tier": ["core"],
            "seller_order_count": [10],
            "seller_avg_delivery_days": [4.1],
            "seller_delay_rate": [0.2],
            "delivery_time_days": [4.1],
            "seller_dispatch_time_days": [1.0],
            "carrier_delivery_time_days": [3.0],
            "estimated_delay_days": [1.0],
            "is_delayed": [True],
            "price": [100.0],
            "freight_value": [15.0],
            "freight_to_price_ratio": [0.15],
            "total_item_value": [115.0],
            "payment_type_mode": ["credit_card"],
            "review_score_mean": [4.5],
            "product_category_name": ["beleza_saude"],
            "product_category_name_english": ["health_beauty"],
            "customer_state": ["SP"],
            "seller_state": ["RJ"],
            "customer_city": ["sao paulo"],
            "customer_zip_code_prefix": [12345],
            "seller_city": ["rio de janeiro"],
            "seller_zip_code_prefix": [22222],
        }
    )

    published = build_published_dashboard_table(source_df)

    assert "customer_id" not in published.columns
    assert "seller_id" not in published.columns
    assert "product_id" not in published.columns
    assert "customer_city" not in published.columns
    assert "customer_zip_code_prefix" not in published.columns
    assert "seller_id" not in published.columns
    assert published.loc[0, "order_id"] != "order-1"
    assert published.loc[0, "customer_unique_id"] != "cust-uniq-1"
    assert published.loc[0, "seller_key"] != "seller-1"
    assert str(published.loc[0, "order_id"]).startswith("order_id_")
    assert str(published.loc[0, "customer_unique_id"]).startswith("customer_unique_id_")
    assert str(published.loc[0, "seller_key"]).startswith("seller_id_")
