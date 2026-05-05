from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Pattern

import pandas as pd
import yaml  # type: ignore[import-untyped]

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

DEFAULT_RULES_PATH = Path("contracts/governance/lgpd_classification_rules.yml")


@dataclass(frozen=True)
class ColumnClassification:
    lgpd_classification: str
    risk_level: str
    recommended_action: str
    reason: str


@dataclass(frozen=True)
class ContractRule:
    lgpd_classification: str
    risk_level: str
    recommended_action: str
    reason: str


@dataclass(frozen=True)
class ClassificationContract:
    exact: dict[str, ContractRule]
    contains: list[tuple[str, ContractRule]]
    regex: list[tuple[Pattern[str], ContractRule]]


def normalize_name(column_name: str) -> str:
    return column_name.strip().lower()


def load_classification_contract(contract_path: str | Path | None = DEFAULT_RULES_PATH) -> ClassificationContract:
    if contract_path is None:
        return ClassificationContract(exact={}, contains=[], regex=[])
    path = Path(contract_path)
    if not path.exists():
        return ClassificationContract(exact={}, contains=[], regex=[])

    content = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    column_rules = content.get("column_rules", {})

    exact_rules: dict[str, ContractRule] = {}
    for column_name, rule in (column_rules.get("exact", {}) or {}).items():
        exact_rules[normalize_name(str(column_name))] = ContractRule(
            lgpd_classification=str(rule["lgpd_classification"]),
            risk_level=str(rule["risk_level"]),
            recommended_action=str(rule["recommended_action"]),
            reason=str(rule["reason"]),
        )

    contains_rules: list[tuple[str, ContractRule]] = []
    for item in (column_rules.get("contains", []) or []):
        contains_rules.append(
            (
                normalize_name(str(item["token"])),
                ContractRule(
                    lgpd_classification=str(item["lgpd_classification"]),
                    risk_level=str(item["risk_level"]),
                    recommended_action=str(item["recommended_action"]),
                    reason=str(item["reason"]),
                ),
            )
        )

    regex_rules: list[tuple[Pattern[str], ContractRule]] = []
    for item in (column_rules.get("regex", []) or []):
        regex_rules.append(
            (
                re.compile(str(item["pattern"])),
                ContractRule(
                    lgpd_classification=str(item["lgpd_classification"]),
                    risk_level=str(item["risk_level"]),
                    recommended_action=str(item["recommended_action"]),
                    reason=str(item["reason"]),
                ),
            )
        )

    return ClassificationContract(exact=exact_rules, contains=contains_rules, regex=regex_rules)


def classify_by_contract(column_name: str, contract: ClassificationContract) -> ColumnClassification | None:
    normalized = normalize_name(column_name)

    exact_match = contract.exact.get(normalized)
    if exact_match is not None:
        return ColumnClassification(
            lgpd_classification=exact_match.lgpd_classification,
            risk_level=exact_match.risk_level,
            recommended_action=exact_match.recommended_action,
            reason=exact_match.reason,
        )

    for token, rule in contract.contains:
        if token in normalized:
            return ColumnClassification(
                lgpd_classification=rule.lgpd_classification,
                risk_level=rule.risk_level,
                recommended_action=rule.recommended_action,
                reason=rule.reason,
            )

    for pattern, rule in contract.regex:
        if pattern.search(column_name):
            return ColumnClassification(
                lgpd_classification=rule.lgpd_classification,
                risk_level=rule.risk_level,
                recommended_action=rule.recommended_action,
                reason=rule.reason,
            )

    return None


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


def classify_dataframe_columns(df: pd.DataFrame, contract_path: str | Path | None = DEFAULT_RULES_PATH) -> pd.DataFrame:
    contract = load_classification_contract(contract_path)
    rows: list[dict[str, object]] = []
    for column_name in df.columns:
        contract_result = classify_by_contract(column_name, contract)
        column_result = contract_result if contract_result is not None else classify_column(column_name, df[column_name])
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
