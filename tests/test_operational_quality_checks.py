from __future__ import annotations

import pandas as pd

from src.quality import QualityCheckResult, run_quality_checks


def _synthetic_fact(row_count: int = 1_001) -> pd.DataFrame:
    order_ids = [f"order-{index}" for index in range(row_count)]
    purchase = pd.Series(pd.Timestamp("2018-01-01"), index=range(row_count))
    approval = pd.Series(pd.Timestamp("2018-01-03"), index=range(row_count))
    delivery = pd.Series(pd.Timestamp("2018-01-04"), index=range(row_count))
    delivery.iloc[0] = pd.Timestamp("2018-01-02")
    return pd.DataFrame(
        {
            "order_id": order_ids,
            "order_item_id": [1] * row_count,
            "customer_id": [f"customer-{index}" for index in range(row_count)],
            "product_id": [f"product-{index}" for index in range(row_count)],
            "seller_id": [f"seller-{index}" for index in range(row_count)],
            "order_purchase_timestamp": purchase,
            "order_approved_at": approval,
            "order_delivered_customer_date": delivery,
            "order_estimated_delivery_date": pd.Timestamp("2018-01-05"),
            "price": [100.0] * row_count,
            "freight_value": [10.0] * row_count,
            "review_score_mean": [5.0] * row_count,
            "product_category_name": ["category"] * row_count,
            "order_year": [2018] * row_count,
            "order_month": [1] * row_count,
            "order_date": pd.Timestamp("2018-01-01"),
            "delivery_time_days": [3.0] * row_count,
            "estimated_delay_days": [-1.0] * row_count,
            "is_delayed": [False] * row_count,
            "total_item_value": [110.0] * row_count,
            "customer_unique_id": [f"unique-{index}" for index in range(row_count)],
            "customer_state": ["SP"] * row_count,
            "seller_state": ["SP"] * row_count,
            "payment_type_mode": ["credit_card"] * row_count,
            "total_payment_value": [110.0] * row_count,
        }
    )


def test_direct_checks_return_historical_type_order_and_thresholds() -> None:
    results = run_quality_checks(_synthetic_fact())
    by_name = {result.check_name: result for result in results}

    assert len(results) == 25
    assert all(isinstance(result, QualityCheckResult) for result in results)
    assert results[0].check_name == "expected_schema"
    assert results[-1].check_name == "record_volume_above_100k"
    assert by_name["review_score_missing_pct"].threshold == 35.0
    assert by_name["category_missing_pct"].threshold == 5.0
    assert by_name["undelivered_orders_pct"].threshold == 5.0
    assert by_name["record_volume_above_100k"].threshold == 100_001


def test_direct_checks_preserve_residual_warn_semantics() -> None:
    results = run_quality_checks(_synthetic_fact())
    warning = next(
        result
        for result in results
        if result.check_name == "temporal_coherence__delivery_before_approval"
    )

    assert warning.status == "WARN"
    assert warning.metric_value == 1
    assert warning.threshold == 0.1
    assert warning.severity == "medium"
    assert "Residual source issue" in warning.details


def test_direct_checks_propagate_failures_without_reordering() -> None:
    fact = _synthetic_fact()
    fact.loc[0, "price"] = -1.0

    results = run_quality_checks(fact)
    negative = results[10]

    assert negative == QualityCheckResult(
        check_name="negative_price_values",
        status="FAIL",
        metric_value=1,
        threshold=0,
        severity="high",
        details="Foram encontrados valores negativos em `price`.",
    )
