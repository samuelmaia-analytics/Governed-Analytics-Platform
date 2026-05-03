from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.governance_history import append_governance_history
from src.governance_types import DataQualityResult, PrivacyRiskResult


def _governance_status(privacy_level: str, failed_checks: int) -> str:
    if privacy_level == "high":
        return "Blocked"
    if privacy_level == "medium" or failed_checks > 0:
        return "Needs Review"
    return "Approved"


def _data_quality_score(quality_results: DataQualityResult) -> int:
    return max(0, 100 - quality_results["failed_checks_count"] * 10)


def save_governance_snapshot(
    *,
    df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
    publication_status: str,
    history_path: Path | None = None,
) -> Path:
    if history_path is not None:
        return append_governance_history(
            total_rows=int(len(df)),
            total_columns=int(df.shape[1]),
            privacy_result=risk_result,
            quality_result=quality_results,
            publication_status=publication_status,
            history_path=history_path,
        )
    return append_governance_history(
        total_rows=int(len(df)),
        total_columns=int(df.shape[1]),
        privacy_result=risk_result,
        quality_result=quality_results,
        publication_status=publication_status,
    )


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

    if publication_status == "Approved":
        st.success(
            f"{'Publication Status' if is_en else 'Status de Publicação'}: {publication_status}",
            icon="✅",
        )
    elif publication_status == "Needs Review":
        st.warning(
            f"{'Publication Status' if is_en else 'Status de Publicação'}: {publication_status}",
            icon="⚠️",
        )
    else:
        st.error(
            f"{'Publication Status' if is_en else 'Status de Publicação'}: {publication_status}",
            icon="⛔",
        )

    charts_col1, charts_col2 = st.columns(2)
    with charts_col1:
        st.markdown("**LGPD Classification Distribution**" if is_en else "**Distribuição de Classificação LGPD**")
        class_counts = (
            classification_df["lgpd_classification"]
            .value_counts()
            .rename_axis("classification")
            .reset_index(name="count")
        )
        fig_class = px.bar(
            class_counts,
            x="classification",
            y="count",
            color="classification",
        )
        fig_class.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_class, width="stretch")

    with charts_col2:
        st.markdown("**Data Quality Checks (PASS vs FAIL)**" if is_en else "**Checks de Qualidade (PASS vs FAIL)**")
        checks_df = pd.DataFrame(quality_results["checks"])
        if checks_df.empty:
            st.info("No quality checks available." if is_en else "Nenhum check de qualidade disponível.")
        else:
            status_counts = checks_df["status"].value_counts().rename_axis("status").reset_index(name="count")
            fig_checks = px.bar(status_counts, x="status", y="count", color="status")
            fig_checks.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_checks, width="stretch")

    st.markdown("**Top Risky Columns**" if is_en else "**Colunas Mais Arriscadas**")
    top_risky_columns = classification_df[
        classification_df["lgpd_classification"].isin(["sensitive_personal_data", "personal_data", "indirect_identifier"])
    ].copy()
    risk_rank = {"sensitive_personal_data": 3, "personal_data": 2, "indirect_identifier": 1}
    top_risky_columns["risk_rank"] = top_risky_columns["lgpd_classification"].map(risk_rank).fillna(0)
    top_risky_columns = top_risky_columns.sort_values(by=["risk_rank", "risk_level", "column_name"], ascending=[False, False, True])
    st.dataframe(
        top_risky_columns[["column_name", "lgpd_classification", "risk_level", "recommended_action", "reason"]].head(10),
        width="stretch",
    )

    with st.expander("Risk Details" if is_en else "Detalhes dos Riscos", expanded=False):
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

    with st.expander("Decision Rationale" if is_en else "Racional da Decisão", expanded=False):
        rationale_lines = [
            (
                f"Privacy risk level `{risk_result['risk_level']}` with score `{risk_result['score']}/100`."
                if is_en
                else f"Nível de risco de privacidade `{risk_result['risk_level']}` com score `{risk_result['score']}/100`."
            ),
            (
                f"Failed quality checks: `{quality_results['failed_checks_count']}`."
                if is_en
                else f"Checks de qualidade reprovados: `{quality_results['failed_checks_count']}`."
            ),
            (
                f"Sensitive columns: `{sensitive_count}`, personal columns: `{personal_count}`, indirect identifiers: `{indirect_count}`."
                if is_en
                else f"Colunas sensíveis: `{sensitive_count}`, pessoais: `{personal_count}`, identificadores indiretos: `{indirect_count}`."
            ),
        ]
        for line in rationale_lines:
            st.write(f"- {line}")

    st.markdown("**Executive Recommendation**" if is_en else "**Recomendação Executiva Final**")
    recommendation_text = (
        "Proceed to publication with routine monitoring."
        if publication_status == "Approved"
        else (
            "Hold publication for control review and remediation actions."
            if publication_status == "Needs Review"
            else "Block publication until privacy controls and quality failures are remediated."
        )
    )
    if not is_en:
        recommendation_text = (
            "Prosseguir com a publicação e monitoramento de rotina."
            if publication_status == "Approved"
            else (
                "Segurar a publicação para revisão de controles e ações de remediação."
                if publication_status == "Needs Review"
                else "Bloquear a publicação até remediar controles de privacidade e falhas de qualidade."
            )
        )
    if publication_status == "Approved":
        st.success(recommendation_text)
    elif publication_status == "Needs Review":
        st.warning(recommendation_text)
    else:
        st.error(recommendation_text)

    button_label = "Save Governance Snapshot" if is_en else "Salvar Snapshot de Governança"
    if st.button(button_label, type="primary"):
        saved_path = save_governance_snapshot(
            df=df,
            risk_result=risk_result,
            quality_results=quality_results,
            publication_status=publication_status,
        )
        if is_en:
            st.success(f"Governance snapshot saved to: {saved_path.resolve()}")
        else:
            st.success(f"Snapshot de governança salvo em: {saved_path.resolve()}")
