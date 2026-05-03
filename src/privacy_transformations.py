from __future__ import annotations

import hashlib
import re

import pandas as pd


def mask_email(value: object) -> str:
    text = str(value or "")
    if "@" not in text:
        return "***"
    local, domain = text.split("@", 1)
    masked_local = f"{local[:1]}***" if local else "***"
    return f"{masked_local}@{domain}"


def mask_cpf(value: object) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) < 11:
        return "***.***.***-**"
    return f"***.***.***-{digits[-2:]}"


def mask_cnpj(value: object) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) < 14:
        return "**.***.***/****-**"
    return f"**.***.***/****-{digits[-2:]}"


def mask_phone(value: object) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) < 4:
        return "****"
    return f"{'*' * (len(digits) - 4)}{digits[-4:]}"


def hash_value(value: object) -> str:
    text = str(value or "")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generalize_date_to_year(value: object) -> str:
    date = pd.to_datetime(value, errors="coerce")
    if pd.isna(date):
        return "unknown_year"
    return str(int(date.year))


def _apply_masking_strategy(column_name: str, series: pd.Series) -> pd.Series:
    lowered = column_name.lower()
    if "email" in lowered:
        return series.map(mask_email)
    if "cpf" in lowered:
        return series.map(mask_cpf)
    if "cnpj" in lowered:
        return series.map(mask_cnpj)
    if "phone" in lowered or "telefone" in lowered:
        return series.map(mask_phone)
    return series.map(hash_value)


def apply_privacy_actions(df: pd.DataFrame, classification_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    transformed_df = df.copy()
    metadata_rows: list[dict[str, str]] = []
    for row in classification_df.itertuples(index=False):
        column_name = str(getattr(row, "column_name"))
        action = str(getattr(row, "recommended_action", "review")).lower()
        if column_name not in transformed_df.columns:
            continue
        if action == "keep":
            metadata_rows.append({"column_name": column_name, "action": "keep", "note": "Column preserved."})
            continue
        if action == "mask":
            transformed_df[column_name] = _apply_masking_strategy(column_name, transformed_df[column_name])
            metadata_rows.append({"column_name": column_name, "action": "mask", "note": "Masked direct identifier."})
            continue
        if action == "anonymize":
            if "date" in column_name.lower() or "data" in column_name.lower():
                transformed_df[column_name] = transformed_df[column_name].map(generalize_date_to_year)
            else:
                transformed_df[column_name] = transformed_df[column_name].map(hash_value)
            metadata_rows.append({"column_name": column_name, "action": "anonymize", "note": "Anonymized values."})
            continue
        if action == "remove":
            transformed_df = transformed_df.drop(columns=[column_name])
            metadata_rows.append({"column_name": column_name, "action": "remove", "note": "Column removed from dataset."})
            continue
        metadata_rows.append({"column_name": column_name, "action": "review", "note": "Column preserved and flagged for review."})
    return transformed_df, pd.DataFrame(metadata_rows)

