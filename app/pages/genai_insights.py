from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale

GENAI_FEATURES_PATH = Path("data/curated/genai/product_text_features.csv")

_EXTRACTION_MODE_LABELS_PT_BR = {
    "openai_api": "API OpenAI — execução registrada",
    "reference": "Saída de referência versionada",
}
_COLUMN_LABELS_PT_BR = {
    "source_id": "ID da origem",
    "title": "Título",
    "category": "Categoria",
    "material": "Material",
    "compatibility": "Compatibilidade",
    "quality_signals": "Sinais de qualidade",
    "functional_features": "Características funcionais",
    "security_features": "Características de segurança",
    "aesthetic_signals": "Sinais estéticos",
    "target_use_cases": "Casos de uso",
    "summary": "Resumo",
    "extraction_mode": "Modo de extração",
    "model_name": "Modelo",
}
_COLUMN_LABELS_EN_US = {
    "source_id": "Source ID",
    "title": "Title",
    "category": "Category",
    "material": "Material",
    "compatibility": "Compatibility",
    "quality_signals": "Quality signals",
    "functional_features": "Functional features",
    "security_features": "Security features",
    "aesthetic_signals": "Aesthetic signals",
    "target_use_cases": "Use cases",
    "summary": "Summary",
    "extraction_mode": "Extraction mode",
    "model_name": "Model",
}


def _extraction_mode_label(value: str, *, is_en: bool) -> str:
    if is_en:
        return value
    return _EXTRACTION_MODE_LABELS_PT_BR.get(value, value)


def _load_genai_features() -> pd.DataFrame:
    if not GENAI_FEATURES_PATH.exists():
        return pd.DataFrame()
    for sep in (";", ","):
        try:
            df = pd.read_csv(GENAI_FEATURES_PATH, sep=sep)
            if "source_id" in df.columns:
                cleaned = df.copy()
                for col in ["source_id", "title", "category"]:
                    if col in cleaned.columns:
                        cleaned[col] = cleaned[col].replace("", pd.NA)
                key_cols = [
                    col
                    for col in ["source_id", "title", "category"]
                    if col in cleaned.columns
                ]
                if key_cols:
                    cleaned = cleaned.dropna(subset=key_cols, how="all")
                return cleaned.reset_index(drop=True)
        except Exception:
            continue
    return pd.DataFrame()


def render_genai_insights(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.title("Generative AI Experiment" if is_en else "Experimento de IA Generativa")
    st.markdown(
        "Exploration of structured attributes extracted from product text and "
        "previously materialized by the pipeline."
        if is_en
        else "Exploração de atributos estruturados extraídos de textos de produto e "
        "materializados previamente no pipeline."
    )
    st.caption(
        "This page presents persisted results. No inference, model call, or API "
        "request is executed when this interface is opened."
        if is_en
        else "Esta página apresenta resultados persistidos. Nenhuma inferência, "
        "chamada de modelo ou API é executada ao abrir esta interface."
    )

    st.markdown(
        "### How to interpret this page"
        if is_en
        else "### Como interpretar esta página"
    )
    st.write(
        "The displayed attributes were generated previously and persisted in a "
        "curated artifact. Extraction mode and model name are metadata recorded in "
        "the file and do not indicate real-time inference."
        if is_en
        else "Os atributos exibidos foram gerados anteriormente e persistidos em um "
        "artefato curado. O modo de extração e o nome do modelo são metadados "
        "registrados no arquivo e não indicam inferência em tempo real."
    )
    st.info(
        "Demonstrative experiment — persisted result, not live inference."
        if is_en
        else "Experimento demonstrativo — resultado persistido, não inferência ao "
        "vivo."
    )

    features_df = _load_genai_features()
    if features_df.empty:
        st.info(
            "Resultado GenAI não disponível neste ambiente."
            if not is_en
            else "GenAI result is not available in this environment."
        )
        st.caption(
            "This page depends on the persisted text-feature artifact."
            if is_en
            else "Esta página depende do artefato persistido de features de texto."
        )
        with st.expander(
            "Experiment technical details"
            if is_en
            else "Detalhes técnicos do experimento"
        ):
            st.caption(
                "Expected artifact path:" if is_en else "Path esperado do artefato:"
            )
            st.code(str(GENAI_FEATURES_PATH))
            st.caption(
                "Controlled generation command:"
                if is_en
                else "Comando técnico de geração controlada:"
            )
            st.code(
                "python -m src.genai_feature_extraction --mode reference",
                language="bash",
            )
        return

    total_items = (
        int(features_df["source_id"].nunique())
        if "source_id" in features_df.columns
        else len(features_df)
    )
    total_categories = (
        int(features_df["category"].nunique())
        if "category" in features_df.columns
        else 0
    )
    extraction_mode = (
        str(features_df["extraction_mode"].mode().iloc[0])
        if "extraction_mode" in features_df.columns
        and not features_df["extraction_mode"].dropna().empty
        else "unknown"
    )
    model_name = (
        str(features_df["model_name"].mode().iloc[0])
        if "model_name" in features_df.columns
        and not features_df["model_name"].dropna().empty
        else "unknown"
    )

    st.markdown("## Summary" if is_en else "## Resumo")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Items processed" if is_en else "Itens processados", total_items)
    m2.metric(
        "Categories identified" if is_en else "Categorias identificadas",
        total_categories,
    )
    m3.caption("Recorded mode" if is_en else "Modo registrado")
    m3.markdown(
        f"**{_extraction_mode_label(extraction_mode, is_en=is_en)}**"
    )
    m4.metric("Recorded model" if is_en else "Modelo registrado", model_name)
    st.caption(
        "Extraction mode and model are metadata persisted in the artifact."
        if is_en
        else "Modo de extração e modelo são metadados persistidos no artefato."
    )
    st.write(
        "The recorded mode describes how the artifact was produced upstream. This "
        "page does not execute that mode again."
        if is_en
        else "O modo registrado descreve como o artefato foi produzido upstream. A "
        "página não executa esse modo novamente."
    )
    st.caption(
        "Model recorded in the source artifact."
        if is_en
        else "Modelo registrado no artefato de origem."
    )

    st.markdown("## Persisted result" if is_en else "## Resultado persistido")
    st.write(
        "The curated file contains one row per source_id after the cleaning applied "
        "by the page."
        if is_en
        else "O arquivo curado contém uma linha por source_id após a limpeza "
        "aplicada "
        "pela página."
    )
    executive_columns = [
        "source_id",
        "title",
        "category",
        "material",
        "compatibility",
        "summary",
    ]
    column_labels = _COLUMN_LABELS_EN_US if is_en else _COLUMN_LABELS_PT_BR
    presentation_df = features_df.loc[:, executive_columns].copy()
    presentation_df = presentation_df.rename(columns=column_labels)
    st.dataframe(presentation_df, width="stretch", hide_index=True)

    st.markdown("## Distribution" if is_en else "## Distribuição")
    if "category" in features_df.columns:
        category_dist = (
            features_df["category"]
            .fillna("unknown")
            .astype(str)
            .value_counts()
            .rename_axis("category")
            .reset_index(name="count")
        )
        category_presentation = category_dist.copy()
        if not is_en:
            category_presentation["category"] = category_presentation[
                "category"
            ].replace({"unknown": "Não informado"})
        if len(features_df) < 3:
            st.markdown(
                "**Category distribution**"
                if is_en
                else "**Distribuição por categoria**"
            )
            for row in category_presentation.itertuples(index=False):
                st.write(f"- {row.category}: {int(row.count)}")
        else:
            fig = px.bar(
                category_presentation,
                x="category",
                y="count",
                color="category",
                title="Distribuição por categoria"
                if not is_en
                else "Category distribution",
            )
            fig.update_layout(
                showlegend=False, margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, width="stretch")

    st.markdown(
        "## Experiment limitations" if is_en else "## Limitações do experimento"
    )
    limitations = (
        (
            "This page does not run inference.",
            "There is no RAG, embedding, or retrieval in this interface.",
            "There is no benchmark or model-quality evaluation.",
            "Tokens, cost, and latency are not available in the interface.",
            f"The current persisted set is small ({len(features_df)} rows).",
        )
        if is_en
        else (
            "A página não executa inferência.",
            "Não há RAG, embeddings ou retrieval nesta interface.",
            "Não há benchmark ou avaliação de qualidade do modelo.",
            "Tokens, custo e latência não estão disponíveis na interface.",
            f"O conjunto persistido atual é pequeno ({len(features_df)} linhas).",
        )
    )
    for limitation in limitations:
        st.write(f"- {limitation}")
    st.caption(
        "Credentials and external integrations are not accessed by this page."
        if is_en
        else "Credenciais e integrações externas não são acessadas por esta "
        "página."
    )

    st.markdown("## Technical details" if is_en else "## Detalhes técnicos")
    with st.expander(
        "Experiment technical details"
        if is_en
        else "Detalhes técnicos do experimento"
    ):
        st.caption(
            "This page reads only the persisted CSV artifact."
            if is_en
            else "Esta página lê somente o artefato CSV persistido."
        )
        st.code(str(GENAI_FEATURES_PATH))
        st.dataframe(features_df.copy(), width="stretch", hide_index=True)
