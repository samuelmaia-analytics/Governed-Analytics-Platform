from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


EXPECTED_PUBLISHED_COLUMNS = [
    "order_id", "order_item_id", "customer_unique_id", "order_status",
    "order_purchase_timestamp", "order_delivered_customer_date",
    "order_estimated_delivery_date", "order_date", "order_year", "order_month",
    "purchase_cohort_month", "cohort_order_month_number", "customer_order_sequence",
    "is_first_order", "seller_key", "seller_volume_tier", "seller_order_count",
    "seller_avg_delivery_days", "seller_delay_rate", "delivery_time_days",
    "seller_dispatch_time_days", "carrier_delivery_time_days", "estimated_delay_days",
    "is_delayed", "price", "freight_value", "freight_to_price_ratio",
    "total_item_value", "payment_type_mode", "review_score_mean",
    "product_category_name", "product_category_name_english", "customer_state",
    "seller_state",
]


def test_published_columns_match_contract() -> None:
    contract = json.loads((ROOT / "contracts" / "published" / "fact_orders_dashboard.contract.json").read_text(encoding="utf-8"))
    assert contract["allow_unexpected_columns"] is False
    assert list(contract["columns"]) == EXPECTED_PUBLISHED_COLUMNS
    assert contract["primary_key"] == ["order_id", "order_item_id"]
