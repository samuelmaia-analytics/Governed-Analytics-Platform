from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_quality_rules import execute_quality_rules, load_quality_rules


def test_all_rule_types_execute() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["A", "A", None],
            "revenue": [100, -2, 2_000_000],
            "order_date": ["2030-01-01", "2024-01-01", "2024-01-02"],
            "customer_email": ["a@x.com", None, None],
            "order_status": ["delivered", "unknown", "shipped"],
        }
    )
    rules = load_quality_rules(Path("contracts/data_quality_rules.yml"))
    checks = execute_quality_rules(df, rules, rule_source="contracts/data_quality_rules.yml")
    names = {check["check_name"] for check in checks}
    assert {
        "order_id_not_null",
        "order_id_unique",
        "revenue_accepted_range",
        "order_date_no_future",
        "revenue_no_negative",
        "customer_email_max_null",
        "order_status_allowed_values",
    }.issubset(names)
    assert any(check["status"] == "FAIL" for check in checks)
    assert all("rule_source" in check for check in checks)

