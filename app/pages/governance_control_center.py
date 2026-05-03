from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.governance_types import DataQualityResult, PrivacyRiskResult


def _governance_status(privacy_level: str, failed_checks: int) -> str:
    if privacy_level == "high":
        return "Blocked"
    if privacy_level == "medium" or failed_checks > 0:
        return "Needs Review"
    return "Approved"


def _data_quality_score(quality_results: DataQualityResult) -> int:
    return max(0, 100 - quality_results["failed_checks_count"] * 10)


def render_governance_control_center(
    df: pd.DataFrame,
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
    locale: Locale,
) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader("Governance Control Center" if is_en else "Central de Controles de Governança")
    privacy_columns = classification_df["lgpd_classification"]
    personal_count = int((privacy_columns == "personal_data").sum())
    sensitive_count = int((privacy_columns == "sensitive_personal_data").sum())
    indirect_count = int((privacy_columns == "indirect_identifier").sum())
    quality_score = _data_quality_score(quality_results)
    governance_status = _governance_status(risk_result["risk_level"], quality_results["failed_checks_count"])
    publication_status = "Approved" if governance_status == "Approved" else ("Needs Review" if governance_status == "Needs Review" else "Blocked")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Governance Status" if is_en else "Status de Governança", governance_status)
    col2.metric("Privacy Risk Score" if is_en else "Score de Risco de Privacidade", f"{risk_result['score']} / 100")
    col3.metric("Data Quality Score" if is_en else "Score de Qualidade", f"{quality_score} / 100")
    col4.metric("Failed Checks" if is_en else "Checks Reprovados", quality_results["failed_checks_count"])

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Personal Columns" if is_en else "Colunas Pessoais", personal_count)
    col6.metric("Sensitive Columns" if is_en else "Colunas Sensíveis", sensitive_count)
    col7.metric("Indirect Identifier Columns" if is_en else "Identificadores Indiretos", indirect_count)
    col8.metric("Publication Readiness" if is_en else "Prontidão para Publicação", publication_status)

    st.markdown("**Top Risks**" if is_en else "**Principais Riscos**")
    failed_checks = [check for check in quality_results["checks"] if check["status"] == "FAIL"]
    if not failed_checks and risk_result["risk_level"] == "low":
        st.write("- No critical governance risks detected." if is_en else "- Nenhum risco crítico de governança detectado.")
    else:
        for check in failed_checks[:5]:
            st.write(f"- {check['check_name']}: {check['recommendation']}")
        if risk_result["risk_level"] in {"medium", "high"}:
            st.write(f"- Privacy risk level is {risk_result['risk_level']} (score {risk_result['score']}).")

    st.markdown("**Recommended Actions**" if is_en else "**Ações Recomendadas**")
    for recommendation in risk_result["recommendations"][:5]:
        st.write(f"- {recommendation}")

    st.markdown("**Executive Summary**" if is_en else "**Resumo Executivo**")
    if is_en:
        st.write(
            f"This dataset has {len(df)} rows and {df.shape[1]} columns. Governance status is {governance_status}. "
            f"Privacy risk is {risk_result['risk_level']} ({risk_result['score']}/100) and data quality score is {quality_score}/100. "
            f"Publication decision: {publication_status}."
        )
    else:
        st.write(
            f"Este dataset possui {len(df)} linhas e {df.shape[1]} colunas. O status de governança é {governance_status}. "
            f"O risco de privacidade é {risk_result['risk_level']} ({risk_result['score']}/100) e o score de qualidade é {quality_score}/100. "
            f"Decisão de publicação: {publication_status}."
        )

