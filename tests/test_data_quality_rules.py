from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_quality_rules import execute_quality_rules, load_quality_rules

RULES_PATH = Path("contracts/data_quality_rules.yml")


def _checks_by_name(df: pd.DataFrame) -> dict[str, dict[str, object]]:
    rules = load_quality_rules(RULES_PATH)
    checks = execute_quality_rules(df, rules, rule_source=str(RULES_PATH))
    return {check["check_name"]: check for check in checks}


def test_not_null_rule() -> None:
    checks = _checks_by_name(pd.DataFrame({"order_id": ["A", None], "revenue": [1, 2], "order_date": ["2024-01-01", "2024-01-01"], "customer_email": ["a@x.com", "b@x.com"], "order_status": ["delivered", "shipped"]}))
    assert checks["order_id_not_null"]["status"] == "FAIL"


def test_unique_rule() -> None:
    checks = _checks_by_name(pd.DataFrame({"order_id": ["A", "A"], "revenue": [1, 2], "order_date": ["2024-01-01", "2024-01-01"], "customer_email": ["a@x.com", "b@x.com"], "order_status": ["delivered", "shipped"]}))
    assert checks["order_id_unique"]["status"] == "FAIL"


def test_accepted_range_rule() -> None:
    checks = _checks_by_name(pd.DataFrame({"order_id": ["A", "B"], "revenue": [100, 2_000_000], "order_date": ["2024-01-01", "2024-01-01"], "customer_email": ["a@x.com", "b@x.com"], "order_status": ["delivered", "shipped"]}))
    assert checks["revenue_accepted_range"]["status"] == "FAIL"


def test_no_future_dates_rule() -> None:
    checks = _checks_by_name(pd.DataFrame({"order_id": ["A", "B"], "revenue": [100, 200], "order_date": ["2030-01-01", "2024-01-01"], "customer_email": ["a@x.com", "b@x.com"], "order_status": ["delivered", "shipped"]}))
    assert checks["order_date_no_future"]["status"] == "FAIL"


def test_no_negative_values_rule() -> None:
    checks = _checks_by_name(pd.DataFrame({"order_id": ["A", "B"], "revenue": [100, -2], "order_date": ["2024-01-01", "2024-01-01"], "customer_email": ["a@x.com", "b@x.com"], "order_status": ["delivered", "shipped"]}))
    assert checks["revenue_no_negative"]["status"] == "FAIL"


def test_max_null_pct_rule() -> None:
    checks = _checks_by_name(pd.DataFrame({"order_id": ["A", "B", "C"], "revenue": [1, 2, 3], "order_date": ["2024-01-01", "2024-01-01", "2024-01-01"], "customer_email": ["a@x.com", None, None], "order_status": ["delivered", "shipped", "processing"]}))
    assert checks["customer_email_max_null"]["status"] == "FAIL"


def test_allowed_values_rule() -> None:
    checks = _checks_by_name(pd.DataFrame({"order_id": ["A", "B"], "revenue": [1, 2], "order_date": ["2024-01-01", "2024-01-01"], "customer_email": ["a@x.com", "b@x.com"], "order_status": ["delivered", "unknown"]}))
    assert checks["order_status_allowed_values"]["status"] == "FAIL"


def test_rule_source_is_present() -> None:
    checks = _checks_by_name(pd.DataFrame({"order_id": ["A"], "revenue": [1], "order_date": ["2024-01-01"], "customer_email": ["a@x.com"], "order_status": ["delivered"]}))
    assert all("rule_source" in check for check in checks.values())
