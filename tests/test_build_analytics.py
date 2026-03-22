from __future__ import annotations

import pandas as pd

from src.build_analytics import derive_columns, remove_obvious_inconsistencies


def test_derive_columns_preserves_null_delay_when_order_is_not_delivered() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["o1"],
            "order_item_id": [1],
            "product_id": ["p1"],
            "seller_id": ["s1"],
            "order_purchase_timestamp": [pd.Timestamp("2018-01-01 10:00:00")],
            "order_delivered_customer_date": [pd.NaT],
            "order_estimated_delivery_date": [pd.Timestamp("2018-01-10")],
            "price": [100.0],
            "freight_value": [15.0],
        }
    )

    result = derive_columns(df)

    assert pd.isna(result.loc[0, "estimated_delay_days"])
    assert bool(result.loc[0, "is_delayed"]) is False
    assert float(result.loc[0, "total_item_value"]) == 115.0


def test_remove_obvious_inconsistencies_filters_negative_values_invalid_delivery_and_duplicates() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2", "o3"],
            "order_item_id": [1, 1, 1, 1],
            "product_id": ["p1", "p1", "p2", "p3"],
            "seller_id": ["s1", "s1", "s2", "s3"],
            "order_purchase_timestamp": [
                pd.Timestamp("2018-01-01 10:00:00"),
                pd.Timestamp("2018-01-01 10:00:00"),
                pd.Timestamp("2018-01-02 10:00:00"),
                pd.Timestamp("2018-01-03 10:00:00"),
            ],
            "price": [100.0, 100.0, -5.0, 40.0],
            "freight_value": [10.0, 10.0, 5.0, 8.0],
            "delivery_time_days": [3.0, 3.0, 2.0, -1.0],
        }
    )

    result = remove_obvious_inconsistencies(df)

    assert len(result) == 1
    assert result.iloc[0]["order_id"] == "o1"

