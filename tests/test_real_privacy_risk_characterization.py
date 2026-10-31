from __future__ import annotations

from typing import Any

import pandas as pd

from src.data_classification import CLASSIFICATION_ROWS
from src.lgpd_classifier import classify_dataframe_columns
from src.publication_evidence import evaluate_sensitive_data_protection
from src.publication_gate import evaluate_publication_readiness
from src.publish_components.models import PrivacyCheck
from src.publish_components.privacy import validate_privacy_controls
from src.publish_dashboard import (
    PUBLISHED_COLUMNS,
    build_published_dashboard_table,
    load_domain_policy,
    load_privacy_contract,
)
from src.risk_scoring import calculate_privacy_risk_score

OPERATIONAL_ROW_COUNT = 112_650


def _representative_source() -> pd.DataFrame:
    values: dict[str, list[Any]] = {
        column: [1] for column in PUBLISHED_COLUMNS if column != "seller_key"
    }
    values.update(
        {
            "order_id": ["order-token"],
            "customer_unique_id": ["customer-token"],
            "seller_id": ["12.345.678/0001-90"],
            "customer_id": ["customer-token"],
            "product_id": ["123.456.789-09"],
            "customer_city": ["city"],
            "seller_city": ["city"],
            "customer_zip_code_prefix": [12345],
            "seller_zip_code_prefix": [12345],
            "customer_state": ["SP"],
            "seller_state": ["SP"],
            "product_category_name": ["books"],
            "product_category_name_english": ["books"],
        }
    )
    return pd.DataFrame(values)


def _scenario() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    list[PrivacyCheck],
]:
    source = _representative_source()
    published = build_published_dashboard_table(source)
    source_classification = classify_dataframe_columns(source)
    published_classification = classify_dataframe_columns(published)
    contract = load_privacy_contract()
    checks = validate_privacy_controls(
        published,
        contract,
        load_domain_policy(contract),
        source_df=source,
        classification_rows=CLASSIFICATION_ROWS,
    )
    return source, published, source_classification, published_classification, checks


def _classes(classification: pd.DataFrame) -> dict[str, str]:
    return dict(
        zip(
            classification["column_name"].astype(str),
            classification["lgpd_classification"].astype(str),
            strict=True,
        )
    )


def test_real_equivalent_inherent_and_residual_scores_are_characterized() -> None:
    _, _, source_classification, published_classification, _ = _scenario()

    inherent = calculate_privacy_risk_score(
        source_classification, OPERATIONAL_ROW_COUNT
    )
    residual = calculate_privacy_risk_score(
        published_classification, OPERATIONAL_ROW_COUNT
    )

    assert inherent["score"] == 86
    assert inherent["score_components"] == {
        "personal_data_exposure": 28,
        "sensitive_data_exposure": 0,
        "indirect_identifier_exposure": 28,
        "critical_null_penalty": 0,
        "direct_identifier_bonus": 15,
        "volume_penalty": 15,
    }
    assert residual["score"] == 53
    assert residual["score_components"] == {
        "personal_data_exposure": 7,
        "sensitive_data_exposure": 0,
        "indirect_identifier_exposure": 16,
        "critical_null_penalty": 0,
        "direct_identifier_bonus": 15,
        "volume_penalty": 15,
    }

    source_classes = _classes(source_classification)
    assert {source_classes[name] for name in {
        "customer_id",
        "customer_unique_id",
        "product_id",
        "seller_id",
    }} == {"personal_data"}
    assert {source_classes[name] for name in {
        "order_id",
        "customer_city",
        "seller_city",
        "customer_zip_code_prefix",
        "seller_zip_code_prefix",
        "customer_state",
        "seller_state",
    }} == {"indirect_identifier"}

    published_classes = _classes(published_classification)
    assert published_classes["customer_unique_id"] == "personal_data"
    assert {published_classes[name] for name in {
        "order_id",
        "seller_key",
        "customer_state",
        "seller_state",
    }} == {"indirect_identifier"}


def test_real_equivalent_privacy_controls_and_protection_are_characterized() -> None:
    _, published, source_classification, _, checks = _scenario()

    assert len(checks) == 16
    assert [check.status for check in checks] == ["PASS"] * 16

    statuses = {check.check_name: check.status for check in checks}
    protected_rows = source_classification[
        source_classification["recommended_action"]
        .astype(str)
        .isin({"mask", "anonymize", "remove"})
    ]
    assert set(protected_rows["column_name"]) == {
        "customer_unique_id",
        "customer_id",
        "product_id",
        "seller_id",
    }
    assert {"customer_id", "product_id", "seller_id"}.isdisjoint(
        published.columns
    )
    assert "customer_unique_id" in published.columns
    assert statuses["pseudonymized__customer_unique_id"] == "PASS"

    protection = evaluate_sensitive_data_protection(
        published, source_classification, checks
    )
    assert protection.evaluated is True
    assert protection.protected is True


def test_only_privacy_score_changes_dual_policy_outcome() -> None:
    common_inputs = {
        "data_quality_score": 100,
        "critical_rule_failures": 0,
        "freshness_status": "fresh",
        "schema_contract_status": "passed",
        "has_sensitive_data_without_protection": False,
    }

    inherent = evaluate_publication_readiness(
        privacy_risk_score=86, **common_inputs
    )
    residual = evaluate_publication_readiness(
        privacy_risk_score=53, **common_inputs
    )

    assert inherent.decision == "Needs Review"
    assert inherent.severity == "High"
    assert inherent.reasons == ["Privacy risk score is elevated (86 >= 60)."]
    assert inherent.required_actions == [
        "Review privacy controls and mitigation actions."
    ]

    assert residual.decision == "Approved"
    assert residual.severity == "Low"
    assert residual.reasons == [
        "All publication controls are within acceptable thresholds."
    ]
    assert residual.required_actions == [
        "Proceed with publication and keep routine monitoring."
    ]
    assert "Blocked" not in {inherent.decision, residual.decision}
