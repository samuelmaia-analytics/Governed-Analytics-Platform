from __future__ import annotations

import pandas as pd
import pytest

from src.lgpd_classifier import classify_dataframe_columns, detect_by_regex
from src.privacy_transformations import apply_privacy_actions


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


@pytest.mark.parametrize(
    ("column", "action"),
    [
        ("health status", "anonymize"),
        ("health-status", "anonymize"),
        ("healthStatus", "anonymize"),
        ("HEALTHStatus", "anonymize"),
        ("biometricTemplate", "remove"),
        ("biometric-template", "remove"),
        ("biometric template", "remove"),
        ("sa\u00fade status", "anonymize"),
        ("sa\u00fade-status", "anonymize"),
        ("sa\u00fadeStatus", "anonymize"),
        ("biom\u00e9tricoTemplate", "remove"),
        ("biom\u00e9trico-template", "remove"),
        ("biom\u00e9trico template", "remove"),
    ],
)
def test_sensitive_header_variants_protect_values_without_renaming_columns(
    column: str, action: str
) -> None:
    source = pd.DataFrame({column: ["synthetic sensitive value"]})
    classification = classify_dataframe_columns(source)
    assert classification["column_name"].tolist() == [column]
    assert classification.iloc[0]["lgpd_classification"] == "sensitive_personal_data"
    assert classification.iloc[0]["recommended_action"] == action
    protected, _ = apply_privacy_actions(source, classification)
    if action == "remove":
        assert column not in protected.columns
    else:
        assert protected[column].iloc[0] != source[column].iloc[0]
    assert source[column].iloc[0] == "synthetic sensitive value"


@pytest.mark.parametrize(
    "column",
    [
        "nome_cliente",
        "nome completo",
        "nome-completo",
        "nomeCompleto",
        "nome do cliente",
        "nome_do_usuario",
        "nomeUsu\u00e1rio",
        "primeiroNome",
        "ultimoNome",
        "nome_pessoa",
        "nome_contato",
    ],
)
def test_portuguese_personal_name_contexts_are_masked(column: str) -> None:
    source = pd.DataFrame({column: ["Pessoa Sintetica"]})
    classification = classify_dataframe_columns(source)
    assert classification.iloc[0]["lgpd_classification"] == "personal_data"
    assert classification.iloc[0]["recommended_action"] == "mask"
    protected, _ = apply_privacy_actions(source, classification)
    assert protected[column].iloc[0] != source[column].iloc[0]


@pytest.mark.parametrize(
    "column",
    [
        "productName",
        "product-category-name",
        "product category name english",
        "category-name",
        "nome_produto",
        "nomeProduto",
        "nome da categoria",
        "nome_categoria_produto",
        "categoriaNome",
    ],
)
def test_product_and_category_names_remain_non_personal(column: str) -> None:
    source = pd.DataFrame({column: ["synthetic label"]})
    classification = classify_dataframe_columns(source)
    assert classification.iloc[0]["lgpd_classification"] == "non_personal"
    assert classification.iloc[0]["recommended_action"] == "keep"
    protected, _ = apply_privacy_actions(source, classification)
    pd.testing.assert_frame_equal(protected, source)


@pytest.mark.parametrize(
    "values",
    [
        ["192.168.1.10", "+55 (11) 99999-9999"],
        ["+55 (11) 99999-9999", "192.168.1.10"],
        ["192.168.1.10; +55 (11) 99999-9999"],
    ],
)
def test_all_regex_matches_prioritize_personal_data_over_ip(values: list[str]) -> None:
    signal, reason = detect_by_regex(pd.Series(values))
    assert signal == "personal_data"
    assert "IP pattern" in reason
    assert "phone pattern" in reason
    source = pd.DataFrame({"network_value": values})
    classification = classify_dataframe_columns(source)
    assert classification.iloc[0]["lgpd_classification"] == "personal_data"
    assert classification.iloc[0]["recommended_action"] == "mask"
    protected, _ = apply_privacy_actions(source, classification)
    assert protected["network_value"].tolist() != source["network_value"].tolist()
