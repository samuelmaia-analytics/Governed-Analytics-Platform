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
    is_en = locale == LOCALE_EN_US
    st.subheader("LGPD & Privacy Risk" if is_en else "LGPD e Risco de Privacidade")

    tab_risk, tab_classification, tab_preview = st.tabs(
        [
            "Score & Risco / Score & Risk",
            "Classificações / Classifications",
            "Prévia de Transformações / Transformation Preview",
        ]
    )

    with tab_risk:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Privacy Risk Score" if is_en else "Score de Risco de Privacidade",
                f"{risk_result['score']} / 100",
            )
        with col2:
            st.metric(
                "Risk Level" if is_en else "Nível de Risco",
                str(risk_result["risk_level"]).upper(),
            )
        st.metric(
            "Publication Recommendation" if is_en else "Recomendação de Publicação",
            str(risk_result.get("publication_recommendation", "needs_review")).upper(),
        )

        components = risk_result.get("score_components", {})
        if components:
            st.markdown("**Score Components**" if is_en else "**Componentes do Score**")
            st.dataframe(
                pd.DataFrame(
                    [
                        {"component": key, "points": value}
                        for key, value in components.items()
                    ]
                ),
                width="stretch",
            )

        st.markdown("**Recommendations**" if is_en else "**Recomendações**")
        for rec in risk_result["recommendations"]:
            st.write(f"- {rec}")

    with tab_classification:
        class_counts = (
            classification_df["lgpd_classification"].value_counts().reset_index()
        )
        class_counts.columns = ["classification", "count"]
        st.bar_chart(class_counts.set_index("classification"))
        st.dataframe(classification_df, width="stretch")

    with tab_preview:
        st.info(
            "Visualize exactly how masking/anonymization will affect the shared dataset."
            if is_en
            else "Visualize exatamente como mascaramento/anonimização afetam o dataset compartilhado."
        )
        transformed_df, metadata_df = apply_privacy_actions(df, classification_df)

        left, right = st.columns(2)
        left.metric(
            "Original Shape" if is_en else "Shape Original",
            f"{df.shape[0]} x {df.shape[1]}",
        )
        right.metric(
            "Transformed Shape" if is_en else "Shape Transformado",
            f"{transformed_df.shape[0]} x {transformed_df.shape[1]}",
        )

        inner_tab1, inner_tab2, inner_tab3 = st.tabs(
            [
                "Resumo de Ações / Actions Summary",
                "Metadados / Metadata",
                "Dataset Protegido / Protected Dataset",
            ]
        )

        with inner_tab1:
            if metadata_df.empty:
                st.info(
                    "No privacy actions were applied."
                    if is_en
                    else "Nenhuma ação de privacidade foi aplicada."
                )
            else:
                actions_summary = (
                    metadata_df["action"]
                    .value_counts()
                    .rename_axis("action")
                    .reset_index(name="count")
                )
                st.dataframe(actions_summary, width="stretch")

        with inner_tab2:
            st.dataframe(metadata_df, width="stretch")

        with inner_tab3:
            st.dataframe(transformed_df.head(50), width="stretch")
            csv_bytes = transformed_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Protected CSV" if is_en else "Baixar CSV Protegido",
                data=csv_bytes,
                file_name="protected_dataset_preview.csv",
                mime="text/csv",
            )
