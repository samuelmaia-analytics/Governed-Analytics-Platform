from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.governance_types import PrivacyRiskResult
from src.privacy_transformations import apply_privacy_actions


def render_lgpd_privacy_risk(
    df: pd.DataFrame,
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    locale: Locale,
) -> None:
    st.subheader("LGPD & Privacy Risk" if locale == LOCALE_EN_US else "LGPD e Risco de Privacidade")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Privacy Risk Score" if locale == LOCALE_EN_US else "Score de Risco de Privacidade", f"{risk_result['score']} / 100")
    with col2:
        st.metric("Risk Level" if locale == LOCALE_EN_US else "Nível de Risco", str(risk_result["risk_level"]).upper())
    st.metric(
        "Publication Recommendation" if locale == LOCALE_EN_US else "Recomendação de Publicação",
        str(risk_result.get("publication_recommendation", "needs_review")).upper(),
    )

    components = risk_result.get("score_components", {})
    if components:
        st.markdown("**Score Components**" if locale == LOCALE_EN_US else "**Componentes do Score**")
        st.dataframe(
            pd.DataFrame(
                [{"component": key, "points": value} for key, value in components.items()]
            ),
            width="stretch",
        )

    class_counts = classification_df["lgpd_classification"].value_counts().reset_index()
    class_counts.columns = ["classification", "count"]
    st.bar_chart(class_counts.set_index("classification"))
    st.dataframe(classification_df, width="stretch")
    st.markdown("**Recommendations**" if locale == LOCALE_EN_US else "**Recomendações**")
    for recommendation in risk_result["recommendations"]:
        st.write(f"- {recommendation}")

    st.divider()
    st.info(
        "Use the Privacy Transformation Preview below to see exactly how masking/anonymization will affect the shared dataset."
        if locale == LOCALE_EN_US
        else "Use a Prévia de Transformações de Privacidade abaixo para visualizar exatamente como mascaramento/anonimização afetam o dataset compartilhado."
    )
    st.markdown("**Privacy Transformation Preview**" if locale == LOCALE_EN_US else "**Prévia de Transformações de Privacidade**")
    transformed_df, metadata_df = apply_privacy_actions(df, classification_df)

    left, right = st.columns(2)
    left.metric(
        "Original Shape" if locale == LOCALE_EN_US else "Shape Original",
        f"{df.shape[0]} x {df.shape[1]}",
    )
    right.metric(
        "Transformed Shape" if locale == LOCALE_EN_US else "Shape Transformado",
        f"{transformed_df.shape[0]} x {transformed_df.shape[1]}",
    )

    st.markdown("**Actions Summary**" if locale == LOCALE_EN_US else "**Resumo de Ações**")
    if metadata_df.empty:
        st.info("No privacy actions were applied." if locale == LOCALE_EN_US else "Nenhuma ação de privacidade foi aplicada.")
    else:
        actions_summary = (
            metadata_df["action"]
            .value_counts()
            .rename_axis("action")
            .reset_index(name="count")
        )
        st.dataframe(actions_summary, width="stretch")

    st.markdown("**Transformation Metadata**" if locale == LOCALE_EN_US else "**Metadados de Transformação**")
    st.dataframe(metadata_df, width="stretch")

    st.markdown("**Protected Dataset Preview**" if locale == LOCALE_EN_US else "**Prévia do Dataset Protegido**")
    st.dataframe(transformed_df.head(50), width="stretch")

    csv_bytes = transformed_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Protected CSV" if locale == LOCALE_EN_US else "Baixar CSV Protegido",
        data=csv_bytes,
        file_name="protected_dataset_preview.csv",
        mime="text/csv",
    )
