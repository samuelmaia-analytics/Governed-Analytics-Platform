from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Pattern

import pandas as pd

PERSONAL_TERMS = {
    "email",
    "cpf",
    "cnpj",
    "phone",
    "telefone",
    "name",
    "nome",
    "address",
    "endereco",
    "birth_date",
    "data_nascimento",
    "ip",
    "user_id",
    "customer_id",
    "document",
    "documento",
    "gender",
    "genero",
}
SENSITIVE_TERMS = {"health", "saude", "biometric", "biometrico"}
INDIRECT_IDENTIFIER_TERMS = {"city", "state", "zip", "postal", "birth", "device", "session"}

REGEX_PATTERNS: dict[str, Pattern[str]] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "cnpj": re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"),
    "phone": re.compile(r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9?\d{4})-?\d{4}"),
    "ip": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}


@dataclass(frozen=True)
class ColumnClassification:
    lgpd_classification: str
    risk_level: str
    recommended_action: str
    reason: str


def normalize_name(column_name: str) -> str:
    return column_name.strip().lower()


def detect_by_column_name(column_name: str) -> tuple[str, str]:
    normalized = normalize_name(column_name)
    if any(term in normalized for term in SENSITIVE_TERMS):
        return "sensitive_personal_data", "Column name indicates sensitive data."
    if any(term in normalized for term in PERSONAL_TERMS):
        return "personal_data", "Column name indicates personal data."
    if any(term in normalized for term in INDIRECT_IDENTIFIER_TERMS):
        return "indirect_identifier", "Column name indicates indirect identification risk."
    return "non_personal", "No personal-data indicators found in column name."


def detect_by_regex(series: pd.Series) -> tuple[str, str]:
    if series.empty:
        return "non_personal", "Column has no values to profile."

    sample_values = series.dropna().astype(str).head(200)
    if sample_values.empty:
        return "non_personal", "Column has only null values."

    joined = " | ".join(sample_values.tolist())
    if REGEX_PATTERNS["email"].search(joined):
        return "personal_data", "Regex matched email pattern in sampled values."
    if REGEX_PATTERNS["cpf"].search(joined):
        return "personal_data", "Regex matched CPF pattern in sampled values."
    if REGEX_PATTERNS["cnpj"].search(joined):
        return "personal_data", "Regex matched CNPJ pattern in sampled values."
    if REGEX_PATTERNS["phone"].search(joined):
        return "personal_data", "Regex matched phone pattern in sampled values."
    if REGEX_PATTERNS["ip"].search(joined):
        return "indirect_identifier", "Regex matched IP pattern in sampled values."
    return "non_personal", "No personal-data regex pattern matched sampled values."


def merge_signal_priority(name_signal: str, regex_signal: str) -> str:
    priority = {
        "sensitive_personal_data": 4,
        "personal_data": 3,
        "indirect_identifier": 2,
        "non_personal": 1,
    }
    return name_signal if priority[name_signal] >= priority[regex_signal] else regex_signal


def map_risk_and_action(classification: str, column_name: str) -> tuple[str, str]:
    lowered = column_name.lower()
    if classification == "sensitive_personal_data":
        if any(token in lowered for token in ["biometric", "biometrico"]):
            return "high", "remove"
        return "high", "anonymize"
    if classification == "personal_data":
        if any(token in lowered for token in ["cpf", "cnpj", "document", "documento"]):
            return "high", "remove"
        return "high", "mask"
    if classification == "indirect_identifier":
        return "medium", "review"
    return "low", "keep"


def classify_column(column_name: str, series: pd.Series) -> ColumnClassification:
    name_signal, name_reason = detect_by_column_name(column_name)
    regex_signal, regex_reason = detect_by_regex(series)
    final_classification = merge_signal_priority(name_signal, regex_signal)
    risk_level, recommended_action = map_risk_and_action(final_classification, column_name)
    reason = f"{name_reason} {regex_reason}".strip()
    return ColumnClassification(
        lgpd_classification=final_classification,
        risk_level=risk_level,
        recommended_action=recommended_action,
        reason=reason,
    )


def classify_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for column_name in df.columns:
        column_result = classify_column(column_name, df[column_name])
        rows.append(
            {
                "column_name": column_name,
                "dtype": str(df[column_name].dtype),
                "lgpd_classification": column_result.lgpd_classification,
                "risk_level": column_result.risk_level,
                "recommended_action": column_result.recommended_action,
                "reason": column_result.reason,
            }
        )
    return pd.DataFrame(rows)
