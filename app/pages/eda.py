from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.eda import (
    correlation_matrix,
    descriptive_statistics,
    detect_outliers_iqr,
    dtype_distribution,
    null_profile,
    top_categories,
)


def render_eda(df: pd.DataFrame, locale: Locale) -> None:
    st.subheader("Exploratory Data Analysis" if locale == LOCALE_EN_US else "Análise Exploratória de Dados")
    st.markdown("**Descriptive Statistics**" if locale == LOCALE_EN_US else "**Estatísticas Descritivas**")
    st.dataframe(descriptive_statistics(df), width="stretch")

    st.markdown("**Data Type Distribution**" if locale == LOCALE_EN_US else "**Distribuição de Tipos de Dados**")
    dtype_df = dtype_distribution(df)
    if not dtype_df.empty:
        st.bar_chart(dtype_df.set_index("dtype")[["count"]])

    st.markdown("**Top Categories**" if locale == LOCALE_EN_US else "**Top Categorias**")
    categories_df = top_categories(df)
    if categories_df.empty:
        st.info("No categorical columns available." if locale == LOCALE_EN_US else "Sem colunas categóricas disponíveis.")
    else:
        st.dataframe(categories_df, width="stretch")

    st.markdown("**Null Profile**" if locale == LOCALE_EN_US else "**Perfil de Nulos**")
    st.dataframe(null_profile(df), width="stretch")

    st.markdown("**Outliers (IQR)**")
    outliers_df = detect_outliers_iqr(df)
    if outliers_df.empty:
        st.info("No numeric columns available for outlier detection." if locale == LOCALE_EN_US else "Sem colunas numéricas para detecção de outliers.")
    else:
        st.dataframe(outliers_df, width="stretch")

    st.markdown("**Correlation Matrix**" if locale == LOCALE_EN_US else "**Matriz de Correlação**")
    corr_df = correlation_matrix(df)
    if corr_df.empty:
        st.info("No numeric columns available for correlation." if locale == LOCALE_EN_US else "Sem colunas numéricas para correlação.")
    else:
        fig = px.imshow(corr_df, text_auto=True, aspect="auto", color_continuous_scale="Blues")
        st.plotly_chart(fig, width="stretch")
