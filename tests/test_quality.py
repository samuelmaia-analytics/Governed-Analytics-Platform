from __future__ import annotations

import pandas as pd

from src.quality import (
    check_dimension_join_coverage,
    check_payment_reconciliation,
)


def build_quality_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "order_item_id": [1, 2, 1],
            "customer_id": ["c1", "c1", "c2"],
            "product_id": ["p1", "p2", "p3"],
            "seller_id": ["s1", "s2", "s3"],
            "order_purchase_timestamp": pd.to_datetime(["2018-01-01", "2018-01-01", "2018-01-02"]),
            "order_approved_at": pd.to_datetime(["2018-01-01", "2018-01-01", "2018-01-02"]),
            "order_delivered_customer_date": pd.to_datetime(["2018-01-05", "2018-01-05", "2018-01-08"]),
            "order_estimated_delivery_date": pd.to_datetime(["2018-01-04", "2018-01-04", "2018-01-07"]),
            "price": [100.0, 50.0, 70.0],
            "freight_value": [10.0, 5.0, 9.0],
            "review_score_mean": [4.0, 4.0, 5.0],
            "product_category_name": ["cat_a", "cat_b", "cat_c"],
            "order_year": [2018, 2018, 2018],
            "order_month": [1, 1, 1],
            "order_date": pd.to_datetime(["2018-01-01", "2018-01-01", "2018-01-02"]),
            "delivery_time_days": [4.0, 4.0, 6.0],
            "estimated_delay_days": [1.0, 1.0, 1.0],
            "is_delayed": [True, True, True],
            "total_item_value": [110.0, 55.0, 79.0],
            "customer_unique_id": ["cu1", "cu1", "cu2"],
            "customer_state": ["SP", "SP", "RJ"],
            "seller_state": ["SP", "MG", "RJ"],
            "payment_type_mode": ["credit_card", "credit_card", "boleto"],
            "total_payment_value": [165.0, 165.0, 79.0],
        }
    )


def test_dimension_join_coverage_fails_when_missing_pct_exceeds_threshold() -> None:
    df = build_quality_frame()
    df.loc[0, "customer_state"] = pd.NA

    results = {result.check_name: result for result in check_dimension_join_coverage(df)}

    assert results["dimension_join_missing_pct__customer_state"].status == "FAIL"
    assert float(results["dimension_join_missing_pct__customer_state"].metric_value) > 1.0


def test_payment_reconciliation_passes_for_reconciled_orders() -> None:
    df = build_quality_frame()

    result = check_payment_reconciliation(df)

    assert result.status == "PASS"
    assert float(result.metric_value) == 0.0


def test_payment_reconciliation_fails_when_gap_exceeds_threshold() -> None:
    df = build_quality_frame()
    df.loc[df["order_id"] == "o2", "total_payment_value"] = 60.0

    result = check_payment_reconciliation(df)

    assert result.status == "FAIL"
    assert float(result.metric_value) > 5.0

