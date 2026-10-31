from __future__ import annotations

import pandas as pd
import pytest

from src.lgpd_classifier import classify_dataframe_columns


@pytest.mark.parametrize(
    ("column", "value", "classification", "risk", "action", "reason_fragment"),
    [
        ("delivery_time_days", 12345678000195, "non_personal", "low", "keep", "skipped"),
        ("seller_dispatch_time_days", 12345678000195, "non_personal", "low", "keep", "skipped"),
        ("carrier_delivery_time_days", 12345678000195, "non_personal", "low", "keep", "skipped"),
        ("estimated_delay_days", 12345678000195, "non_personal", "low", "keep", "skipped"),
        ("seller_avg_delivery_days", 12345678000195, "non_personal", "low", "keep", "skipped"),
        ("seller_delay_rate", 12345678000195, "non_personal", "low", "keep", "skipped"),
        ("total_item_value", 12345678000195, "non_personal", "low", "keep", "skipped"),
        ("freight_to_price_ratio", 12345678000195, "non_personal", "low", "keep", "skipped"),
        ("order_id", "11999999999", "indirect_identifier", "medium", "review", "technical-identifier"),
        ("customer_unique_id", "11999999999", "personal_data", "high", "mask", "technical-identifier"),
        ("seller_key", "11999999999", "indirect_identifier", "medium", "review", "technical-identifier"),
        ("product_category_name", "books", "non_personal", "low", "keep", "No personal-data"),
        ("product_category_name_english", "books", "non_personal", "low", "keep", "No personal-data"),
    ],
)
def test_corrected_classifier_cases_are_characterized(
    column: str,
    value: object,
    classification: str,
    risk: str,
    action: str,
    reason_fragment: str,
) -> None:
    result = classify_dataframe_columns(pd.DataFrame({column: [value]})).iloc[0]

    assert result["lgpd_classification"] == classification
    assert result["risk_level"] == risk
    assert result["recommended_action"] == action
    assert reason_fragment in result["reason"]
