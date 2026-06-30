from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_quality_rules import execute_quality_rules, load_quality_rules
from src.lgpd_classifier import classify_dataframe_columns
from src.publication_gate import evaluate_publication_readiness
from src.risk_scoring import calculate_privacy_risk_score

FIXTURES_DIR = Path(__file__).parent / "fixtures"
RULES_PATH = Path("contracts/data_quality_rules.yml")
REQUIRED_COLUMNS = {
    "order_id",
    "customer_id",
    "customer_email",
    "order_status",
    "order_date",
    "revenue",
}


def _load_fixture(name: str) -> pd.DataFrame:
    return pd.read_csv(FIXTURES_DIR / name)


def _quality_score_from_rules(df: pd.DataFrame) -> tuple[int, int]:
    checks = execute_quality_rules(df, load_quality_rules(RULES_PATH), rule_source="fixture")
    failed_checks = sum(check["status"] == "FAIL" for check in checks)
    return max(0, 100 - failed_checks * 10), failed_checks


def test_valid_fixture_is_approved_by_publication_controls() -> None:
    df = _load_fixture("valid_dataset.csv")
    quality_score, failed_checks = _quality_score_from_rules(df)
    risk_result = calculate_privacy_risk_score(
        classify_dataframe_columns(df),
        total_rows=len(df),
    )

    result = evaluate_publication_readiness(
        data_quality_score=quality_score,
        privacy_risk_score=int(risk_result["score"]),
        critical_rule_failures=failed_checks,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )

    assert result.decision == "Approved"


def test_missing_required_customer_id_needs_review_or_blocks_publication() -> None:
    df = _load_fixture("invalid_missing_customer_id.csv")
    missing_customer_ids = int(df["customer_id"].isna().sum())

    result = evaluate_publication_readiness(
        data_quality_score=85,
        privacy_risk_score=35,
        critical_rule_failures=missing_customer_ids,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )

    assert missing_customer_ids > 0
    assert result.decision in {"Needs Review", "Blocked"}
    assert result.decision == "Blocked"


def test_schema_change_blocks_publication() -> None:
    df = _load_fixture("invalid_schema_change.csv")
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=20,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="failed" if missing_columns else "passed",
        has_sensitive_data_without_protection=False,
    )

    assert missing_columns == {"order_id"}
    assert result.decision == "Blocked"


def test_high_lgpd_risk_fixture_needs_review_or_blocks_publication() -> None:
    df = _load_fixture("high_lgpd_risk_dataset.csv")
    risk_result = calculate_privacy_risk_score(
        classify_dataframe_columns(df),
        total_rows=100_000,
    )

    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=int(risk_result["score"]),
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=risk_result["risk_level"] == "high",
    )

    assert int(risk_result["score"]) > 60
    assert result.decision in {"Needs Review", "Blocked"}
