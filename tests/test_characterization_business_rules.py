from __future__ import annotations

from dataclasses import asdict, fields

import pandas as pd

import src.business_rule_validation as rules
from src.business_rule_validation import BusinessRuleResult


def _contract(rule_items: list[dict]) -> dict:
    return {
        "contract_id": "characterization",
        "version": 1,
        "dataset_name": "demo",
        "owner": "owner",
        "rules": rule_items,
    }


def test_all_five_runner_types_and_result_order_are_characterized() -> None:
    df = pd.DataFrame(
        {
            "price": [10.0, -1.0],
            "status": ["delivered", "invalid"],
            "delivered_at": [pd.Timestamp("2020-01-02"), pd.NaT],
            "purchased_at": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-03")],
        }
    )
    contract = _contract(
        [
            {"rule_id": "range", "severity": "high", "type": "range", "column": "price", "params": {"min": 0}},
            {"rule_id": "conditional", "severity": "high", "type": "not_null_if", "column": "delivered_at", "params": {"if_column": "status", "if_equals": "delivered"}},
            {"rule_id": "values", "severity": "medium", "type": "accepted_values", "column": "status", "params": {"allowed": ["delivered"]}},
            {"rule_id": "compare", "severity": "high", "type": "compare_columns", "columns": ["delivered_at", "purchased_at"], "params": {"operator": ">="}},
            {"rule_id": "expression", "severity": "low", "type": "expression", "params": {"expression": "price >= 0"}},
        ]
    )

    results = rules.run_business_rules(df, contract)

    assert [result.rule_id for result in results] == [
        "range",
        "conditional",
        "values",
        "compare",
        "expression",
    ]
    assert [result.status for result in results] == [
        "FAIL",
        "PASS",
        "FAIL",
        "PASS",
        "FAIL",
    ]
    assert [result.failed_rows for result in results] == [1, 0, 1, 0, 1]


def test_failure_tolerance_preserves_pass_with_residual_failures() -> None:
    df = pd.DataFrame({"value": [1.0] * 99 + [-1.0]})
    within = _contract(
        [{"rule_id": "tolerated", "severity": "high", "type": "range", "column": "value", "description": "non-negative", "params": {"min": 0, "max_failure_pct": 1.0}}]
    )
    exceeded = _contract(
        [{"rule_id": "blocked", "severity": "high", "type": "range", "column": "value", "description": "non-negative", "params": {"min": 0, "max_failure_pct": 0.99}}]
    )

    tolerated = rules.run_business_rules(df, within)[0]
    blocked = rules.run_business_rules(df, exceeded)[0]

    assert asdict(tolerated) == {
        "rule_id": "tolerated",
        "status": "PASS",
        "severity": "high",
        "failed_rows": 1,
        "failure_pct": 1.0,
        "details": "non-negative Falha residual dentro da tolerancia contratual de 1.0%.",
    }
    assert blocked.status == "FAIL"
    assert blocked.failed_rows == 1
    assert blocked.failure_pct == 1.0


def test_business_rule_result_and_public_runners_remain_stable() -> None:
    assert [field.name for field in fields(BusinessRuleResult)] == [
        "rule_id",
        "status",
        "severity",
        "failed_rows",
        "failure_pct",
        "details",
    ]
    assert all(
        callable(api)
        for api in [
            rules.load_fact_table,
            rules.load_contract,
            rules.run_business_rules,
            rules.save_results,
            rules.render_report,
            rules.save_report,
        ]
    )
