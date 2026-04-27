from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.cards import render_metric_cards
from app.i18n import LOCALE_EN_US, Locale
from src.governance_types import DataQualityResult, PrivacyRiskResult


def render_executive_overview(
    df: pd.DataFrame,
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
    locale: Locale,
) -> None:
    personal_fields = int(
        classification_df["lgpd_classification"].isin(["personal_data", "sensitive_personal_data"]).sum()
    )
    status = (
        ("Healthy" if quality_results["failed_checks_count"] == 0 else "Attention Required")
        if locale == LOCALE_EN_US
        else ("Saudável" if quality_results["failed_checks_count"] == 0 else "Requer Atenção")
    )
    metrics = [
        {"label": "Datasets Analyzed" if locale == LOCALE_EN_US else "Datasets Analisados", "value": "1"},
        {"label": "Total Columns" if locale == LOCALE_EN_US else "Total de Colunas", "value": str(df.shape[1])},
        {"label": "Personal Fields" if locale == LOCALE_EN_US else "Campos Pessoais", "value": str(personal_fields)},
        {"label": "LGPD Risk Score", "value": str(risk_result["score"])},
        {"label": "Quality Failures" if locale == LOCALE_EN_US else "Falhas de Qualidade", "value": str(quality_results["failed_checks_count"])},
        {"label": "Governance Status" if locale == LOCALE_EN_US else "Status Governança", "value": status},
    ]
    render_metric_cards(metrics)

    st.subheader("Executive Summary" if locale == LOCALE_EN_US else "Resumo Executivo")
    if locale == LOCALE_EN_US:
        st.write(
            f"The dataset has {len(df)} rows and {df.shape[1]} columns. "
            f"The current LGPD risk is **{risk_result['risk_level']}** with a score of **{risk_result['score']}**."
        )
    else:
        st.write(
            f"O dataset possui {len(df)} registros e {df.shape[1]} colunas. "
            f"O risco LGPD atual é **{risk_result['risk_level']}** com score **{risk_result['score']}**."
        )
