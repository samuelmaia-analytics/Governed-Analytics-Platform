from __future__ import annotations

import pandas as pd
import pytest

from src.business_rule_validation import run_business_rules


def build_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "price": [10.0, -1.0],
            "freight_value": [2.0, 3.0],
            "order_status": ["delivered", "unknown"],
            "order_delivered_customer_date": [pd.Timestamp("2020-01-02"), pd.NaT],
            "order_purchase_timestamp": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-03")],
        }
    )


def test_run_business_rules_evaluates_multiple_types() -> None:
    contract = {
        "contract_id": "x",
        "version": 1,
        "dataset_name": "fact_orders_enriched",
        "owner": "owner",
        "rules": [
            {"rule_id": "r1", "severity": "high", "type": "range", "column": "price", "params": {"min": 0}},
            {
                "rule_id": "r2",
                "severity": "high",
                "type": "not_null_if",
                "column": "order_delivered_customer_date",
                "params": {"if_column": "order_status", "if_equals": "delivered"},
            },
            {
                "rule_id": "r3",
                "severity": "medium",
                "type": "accepted_values",
                "column": "order_status",
                "params": {"allowed": ["delivered", "unknown"]},
            },
            {
                "rule_id": "r4",
                "severity": "high",
                "type": "compare_columns",
                "columns": ["order_delivered_customer_date", "order_purchase_timestamp"],
                "params": {"operator": ">="},
            },
        ],
    }

    results = {result.rule_id: result for result in run_business_rules(build_df(), contract)}

    assert results["r1"].status == "FAIL"
    assert results["r2"].status == "PASS"
    assert results["r3"].status == "PASS"
    assert results["r4"].status == "PASS"


def test_run_business_rules_raises_for_invalid_contract() -> None:
    with pytest.raises(ValueError, match="Campos ausentes"):
        run_business_rules(build_df(), {"rules": []})

