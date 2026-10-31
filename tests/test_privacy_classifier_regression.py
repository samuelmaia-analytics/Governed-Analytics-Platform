from __future__ import annotations

import pandas as pd
import pytest

from src.lgpd_classifier import classify_dataframe_columns, detect_by_regex


def _classification(column: str, value: object) -> str:
    result = classify_dataframe_columns(pd.DataFrame({column: [value]})).iloc[0]
    return str(result["lgpd_classification"])


@pytest.mark.parametrize(
    ("column", "value", "expected"),
    [
        ("cpf_value", "123.456.789-09", "personal_data"),
        ("cnpj_value", "12.345.678/0001-90", "personal_data"),
        ("contact_phone", "+55 (11) 99999-9999", "personal_data"),
        ("contact_email", "ana@example.com", "personal_data"),
        ("network_value", "192.168.1.10", "indirect_identifier"),
        ("customer_name", "Ana", "personal_data"),
        ("health_status", "monitorado", "sensitive_personal_data"),
    ],
)
def test_true_positive_detection_is_preserved(
    column: str, value: object, expected: str
) -> None:
    assert _classification(column, value) == expected


def test_value_regex_is_applied_to_each_sample_independently() -> None:
    classification, reason = detect_by_regex(
        pd.Series(["ordinary text", "ana@example.com", "more text"])
    )

    assert classification == "personal_data"
    assert "email" in reason


def test_personal_name_signal_keeps_priority_over_ip_value_signal() -> None:
    assert _classification("network_address", "192.168.1.10") == "personal_data"


@pytest.mark.parametrize(
    "column",
    ["product_category_name", "product_category_name_english", "shipping_limit_date"],
)
def test_generic_name_and_ip_substrings_do_not_imply_personal_data(
    column: str,
) -> None:
    assert _classification(column, "ordinary") == "non_personal"


def test_numeric_values_that_look_like_cnpj_are_not_identifiers() -> None:
    classification, reason = detect_by_regex(pd.Series([12345678000195]))

    assert classification == "non_personal"
    assert "skipped" in reason


@pytest.mark.parametrize(
    ("column", "expected"),
    [
        ("order_id", "indirect_identifier"),
        ("customer_unique_id", "personal_data"),
        ("seller_key", "indirect_identifier"),
    ],
)
def test_governed_technical_identifier_classification(
    column: str, expected: str
) -> None:
    assert _classification(column, "11999999999") == expected
