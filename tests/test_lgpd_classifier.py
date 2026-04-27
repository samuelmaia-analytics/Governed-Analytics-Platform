from __future__ import annotations

import pandas as pd

from src.lgpd_classifier import classify_dataframe_columns


def _class_of(result_df: pd.DataFrame, column_name: str) -> pd.Series:
    return result_df.loc[result_df["column_name"] == column_name].iloc[0]


def test_detects_email_as_personal_data() -> None:
    df = pd.DataFrame({"customer_email": ["ana@example.com"]})
    result = classify_dataframe_columns(df)
    assert _class_of(result, "customer_email")["lgpd_classification"] == "personal_data"


def test_detects_cpf_as_personal_data() -> None:
    df = pd.DataFrame({"cpf": ["123.456.789-09"]})
    result = classify_dataframe_columns(df)
    assert _class_of(result, "cpf")["lgpd_classification"] == "personal_data"


def test_detects_health_as_sensitive_personal_data() -> None:
    df = pd.DataFrame({"saude_status": ["monitorado"]})
    result = classify_dataframe_columns(df)
    assert _class_of(result, "saude_status")["lgpd_classification"] == "sensitive_personal_data"


def test_classifies_revenue_as_non_personal() -> None:
    df = pd.DataFrame({"revenue": [100.0, 200.0]})
    result = classify_dataframe_columns(df)
    assert _class_of(result, "revenue")["lgpd_classification"] == "non_personal"


def test_returns_coherent_recommended_action() -> None:
    df = pd.DataFrame({"customer_email": ["ana@example.com"], "revenue": [100.0]})
    result = classify_dataframe_columns(df)
    assert _class_of(result, "customer_email")["recommended_action"] in {"mask", "review", "anonymize"}
    assert _class_of(result, "revenue")["recommended_action"] == "keep"
