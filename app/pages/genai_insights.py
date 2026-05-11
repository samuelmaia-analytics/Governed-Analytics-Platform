from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale

GENAI_FEATURES_PATH = Path("data/curated/genai/product_text_features.csv")


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
                key_cols = [col for col in ["source_id", "title", "category"] if col in cleaned.columns]
                if key_cols:
                    cleaned = cleaned.dropna(subset=key_cols, how="all")
                return cleaned.reset_index(drop=True)
        except Exception:
            continue
    return pd.DataFrame()


def render_genai_insights(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader("GenAI Product Text Intelligence")

    features_df = _load_genai_features()
    if features_df.empty:
        st.info(
            "Sem artefatos de GenAI. Execute `python -m src.genai_feature_extraction --mode reference`."
            if not is_en
            else "No GenAI artifacts found. Run `python -m src.genai_feature_extraction --mode reference`."
        )
        return

    total_items = int(features_df["source_id"].nunique()) if "source_id" in features_df.columns else len(features_df)
    total_categories = int(features_df["category"].nunique()) if "category" in features_df.columns else 0
    extraction_mode = (
        str(features_df["extraction_mode"].mode().iloc[0])
        if "extraction_mode" in features_df.columns and not features_df["extraction_mode"].dropna().empty
        else "unknown"
    )
    model_name = (
        str(features_df["model_name"].mode().iloc[0])
        if "model_name" in features_df.columns and not features_df["model_name"].dropna().empty
        else "unknown"
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Items", total_items)
    m2.metric("Categories", total_categories)
    m3.metric("Extraction Mode", extraction_mode)
    m4.metric("Model", model_name)

    if "category" in features_df.columns:
        category_dist = (
            features_df["category"]
            .fillna("unknown")
            .astype(str)
            .value_counts()
            .rename_axis("category")
            .reset_index(name="count")
        )
        if len(features_df) < 3:
            st.markdown(
                "**Resumo de Categorias**" if not is_en else "**Category Summary**"
            )
            for row in category_dist.itertuples(index=False):
                st.write(f"- {row.category}: {int(row.count)}")
        else:
            fig = px.bar(
                category_dist,
                x="category",
                y="count",
                color="category",
                title="Distribuição de Categorias Extraídas"
                if not is_en
                else "Extracted Category Distribution",
            )
            fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Feature Inventory**" if is_en else "**Inventário de Features**")
    st.dataframe(features_df, width="stretch")
