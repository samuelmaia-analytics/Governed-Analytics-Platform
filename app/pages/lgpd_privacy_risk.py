from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.governance_types import PrivacyRiskResult
from src.privacy_transformations import apply_privacy_actions

_RISK_LEVEL_LABELS = {
    "low": "BAIXO",
    "medium": "MÉDIO",
    "high": "ALTO",
}

_PUBLICATION_RECOMMENDATION_LABELS = {
    "approved": "APROVADO",
    "needs_review": "REVISÃO NECESSÁRIA",
    "blocked": "BLOQUEADO",
}

_RECOMMENDATION_LABELS = {
    "Apply masking for direct identifiers in shared datasets.": (
        "Aplicar mascaramento aos identificadores diretos em datasets "
        "compartilhados."
    ),
    "Anonymize or remove sensitive columns from executive layers.": (
        "Anonimizar ou remover colunas sensíveis das camadas executivas."
    ),
    "Review null patterns in critical personal-data columns.": (
        "Revisar padrões de valores nulos em colunas críticas de dados pessoais."
    ),
    "Document legal basis and retention policy for personal data usage.": (
        "Documentar a base legal e a política de retenção para uso de dados "
        "pessoais."
    ),
    "Block publication until masking/anonymization controls are implemented.": (
        "Bloquear a publicação até que os controles de mascaramento ou "
        "anonimização estejam implementados."
    ),
}


def _display_label(value: object, labels: dict[str, str]) -> str:
    raw_value = str(value)
    return labels.get(raw_value.lower(), raw_value.upper())


def _display_recommendation(recommendation: str) -> str:
    return _RECOMMENDATION_LABELS.get(recommendation, recommendation)


def render_lgpd_privacy_risk(
    df: pd.DataFrame,
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    locale: Locale,
) -> None:
    is_en = locale == LOCALE_EN_US
    st.title("Privacidade e Controles LGPD")
    st.markdown(
        "Visão demonstrativa dos riscos de privacidade, classificações de dados "
        "e controles aplicados ao pipeline analítico."
    )
    st.caption(
        "Os indicadores abaixo representam uma avaliação diagnóstica do cenário "
        "demonstrativo e não substituem uma análise jurídica ou RIPD formal."
    )
    st.markdown("### Como interpretar esta página")
    st.write(
        "A página demonstra como a plataforma identifica dados pessoais e "
        "sensíveis, calcula risco de privacidade e aplica recomendações de "
        "governança antes da publicação analítica."
    )

    tab_risk, tab_classification, tab_preview = st.tabs(
        [
            "Score e risco",
            "Classificações",
            "Prévia de transformações",
        ]
    )

    with tab_risk:
        st.subheader("Avaliação diagnóstica de privacidade")
        st.info(
            "O cenário demonstrativo evidencia como a plataforma identifica "
            "riscos elevados e pode recomendar bloqueio de publicação quando "
            "controles de proteção ainda não estão considerados na avaliação."
        )
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Score de risco de privacidade",
                f"{risk_result['score']} / 100",
            )
        with col2:
            st.metric(
                "Nível de risco",
                _display_label(risk_result["risk_level"], _RISK_LEVEL_LABELS),
            )
        st.metric(
            "Recomendação de publicação",
            _display_label(
                risk_result.get("publication_recommendation", "needs_review"),
                _PUBLICATION_RECOMMENDATION_LABELS,
            ),
        )

        components = risk_result.get("score_components", {})
        if components:
            with st.expander(
                "Componentes técnicos do score",
                expanded=False,
            ):
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"component": key, "points": value}
                            for key, value in components.items()
                        ]
                    ),
                    width="stretch",
                )

        st.markdown("**Recomendações**")
        for rec in risk_result["recommendations"]:
            st.write(f"- {_display_recommendation(rec)}")

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
