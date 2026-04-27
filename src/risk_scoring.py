from __future__ import annotations

from typing import SupportsInt, cast

import pandas as pd

from src.governance_types import PrivacyRiskResult


def _coerce_int(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    if hasattr(value, "__int__"):
        try:
            return int(cast(SupportsInt, value))
        except (TypeError, ValueError):
            return 0
    return 0


def _risk_level_from_score(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 70:
        return "medium"
    return "high"


def calculate_privacy_risk_score(classification_df: pd.DataFrame, total_rows: int) -> PrivacyRiskResult:
    if classification_df.empty:
        return {
            "score": 0,
            "risk_level": "low",
            "summary": "No columns found for privacy evaluation.",
            "recommendations": ["Validate the dataset schema before publishing."],
        }

    class_counts = classification_df["lgpd_classification"].value_counts()
    personal_count = _coerce_int(class_counts.get("personal_data", 0))
    sensitive_count = _coerce_int(class_counts.get("sensitive_personal_data", 0))
    indirect_count = _coerce_int(class_counts.get("indirect_identifier", 0))

    critical_df = classification_df[
        classification_df["lgpd_classification"].isin(["personal_data", "sensitive_personal_data"])
    ].copy()
    null_penalty = 0
    if "null_pct" in classification_df.columns and not critical_df.empty:
        critical_null_avg = float(critical_df["null_pct"].fillna(0).mean())
        null_penalty = min(15, int(round(critical_null_avg * 0.2)))

    direct_identifier_bonus = 0
    direct_hint = classification_df["column_name"].astype(str).str.contains(
        "cpf|email|phone|telefone|document|nome|name|cnpj",
        case=False,
        regex=True,
    )
    if bool(direct_hint.any()):
        direct_identifier_bonus = 15

    volume_penalty = 0
    if total_rows >= 100_000:
        volume_penalty = 15
    elif total_rows >= 10_000:
        volume_penalty = 10
    elif total_rows >= 1_000:
        volume_penalty = 5

    raw_score = (
        personal_count * 7
        + sensitive_count * 15
        + indirect_count * 4
        + null_penalty
        + direct_identifier_bonus
        + volume_penalty
    )
    score = max(0, min(100, int(raw_score)))
    risk_level = _risk_level_from_score(score)

    recommendations = [
        "Apply masking for direct identifiers in shared datasets.",
        "Anonymize or remove sensitive columns from executive layers.",
        "Review null patterns in critical personal-data columns.",
        "Document legal basis and retention policy for personal data usage.",
    ]
    if risk_level == "low":
        recommendations = [
            "Keep recurring LGPD checks in CI to prevent regressions.",
            "Maintain data dictionary and ownership metadata updated.",
        ]

    summary = (
        f"Dataset with {personal_count} personal, {sensitive_count} sensitive and "
        f"{indirect_count} indirect identifier columns over {total_rows} rows."
    )
    return {
        "score": score,
        "risk_level": risk_level,
        "summary": summary,
        "recommendations": recommendations,
    }
