from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from src.data_quality_rules import (
    DataQualityRule,
    execute_quality_rules,
    load_quality_rules,
)


def _rule(name: str, rule_type: str, column: str, **params) -> DataQualityRule:
    return DataQualityRule(name, rule_type, [column], "high", params, "remediate")


def test_current_yaml_contract_names_types_and_defaults() -> None:
    rules = load_quality_rules(Path("contracts/data_quality_rules.yml"))

    assert [(rule.name, rule.rule_type) for rule in rules] == [
        ("order_id_not_null", "not_null"),
        ("order_id_unique", "unique"),
        ("revenue_accepted_range", "accepted_range"),
        ("order_date_no_future", "no_future_dates"),
        ("revenue_no_negative", "no_negative_values"),
        ("customer_email_max_null", "max_null_pct"),
        ("order_status_allowed_values", "allowed_values"),
        ("order_status_not_null", "not_null"),
        ("order_date_max_null", "max_null_pct"),
    ]
    assert len(rules) == 9


def test_all_supported_yaml_rule_types_preserve_results() -> None:
    future = pd.Timestamp(datetime.now(timezone.utc) + timedelta(days=1)).tz_localize(
        None
    )
    df = pd.DataFrame(
        {
            "required": [1, None],
            "identifier": ["x", "x"],
            "bounded": [1.0, 11.0],
            "event_date": [pd.Timestamp("2020-01-01"), future],
            "amount": [1.0, -1.0],
            "nullable": [None, "x"],
            "status": ["ok", "bad"],
        }
    )
    rules = [
        _rule("not_null", "not_null", "required"),
        _rule("unique", "unique", "identifier"),
        _rule("range", "accepted_range", "bounded", min=0, max=10),
        _rule("future", "no_future_dates", "event_date"),
        _rule("negative", "no_negative_values", "amount"),
        _rule("null_pct", "max_null_pct", "nullable", max_null_pct=40),
        _rule("allowed", "allowed_values", "status", allowed=["ok"]),
    ]

    checks = execute_quality_rules(df, rules, rule_source="fixture.yml")

    assert [check["check_name"] for check in checks] == [rule.name for rule in rules]
    assert [check["status"] for check in checks] == ["FAIL"] * 7
    assert [check["affected_rows"] for check in checks] == [1, 2, 1, 1, 1, 2, 1]
    assert all(check["severity"] == "high" for check in checks)
    assert all(check["rule_source"] == "fixture.yml" for check in checks)


def test_missing_column_fails_but_unknown_rule_with_existing_column_is_ignored() -> None:
    missing = _rule("missing", "not_null", "absent")
    unknown = _rule("unknown", "future_rule_type", "present")

    checks = execute_quality_rules(
        pd.DataFrame({"present": [1]}), [missing, unknown], rule_source="fixture.yml"
    )

    assert checks == [
        {
            "check_name": "missing",
            "status": "FAIL",
            "severity": "high",
            "affected_columns": "absent",
            "affected_rows": 0,
            "recommendation": "remediate",
            "rule_source": "fixture.yml",
        }
    ]


def test_yaml_and_business_contract_status_allowlists_are_currently_different() -> None:
    yaml_rule = next(
        rule
        for rule in load_quality_rules("contracts/data_quality_rules.yml")
        if rule.name == "order_status_allowed_values"
    )
    import json

    business = json.loads(
        Path(
            "contracts/governance/business_rules/fact_orders_enriched.v1.json"
        ).read_text(encoding="utf-8")
    )
    business_rule = next(
        rule for rule in business["rules"] if rule["rule_id"] == "order_status_whitelist"
    )

    assert yaml_rule.params["allowed"] == [
        "delivered",
        "shipped",
        "canceled",
        "processing",
    ]
    assert business_rule["params"]["allowed"] == [
        "approved",
        "canceled",
        "created",
        "delivered",
        "invoiced",
        "processing",
        "shipped",
        "unavailable",
        "unknown",
    ]
