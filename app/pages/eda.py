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

try:
    from src.eda import generate_storytelling_insights, run_statistical_tests
except ImportError:
    def generate_storytelling_insights(_df: pd.DataFrame) -> list[str]:
        return []

    def run_statistical_tests(_df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame()


def _render_overview(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    insights = generate_storytelling_insights(df)
    st.markdown(
        "**Narrative Insights**" if is_en else "**Insights Narrativos**"
    )
    if insights:
        for insight in insights:
            st.write(f"- {insight}")
    else:
        st.info(
            "No narrative insights available for this dataset."
            if is_en
            else "Sem insights narrativos disponíveis para este dataset."
        )

    st.markdown(
        "**Estatísticas Descritivas**" if not is_en else "**Descriptive Statistics**"
    )
    st.dataframe(descriptive_statistics(df), width="stretch")

    st.markdown(
        "**Distribuição de Tipos de Dados**"
        if not is_en
        else "**Data Type Distribution**"
    )
    dtype_df = dtype_distribution(df)
    if not dtype_df.empty:
        st.bar_chart(dtype_df.set_index("dtype")[["count"]])

    st.markdown("**Top Categorias**" if not is_en else "**Top Categories**")
    categories_df = top_categories(df)
    if categories_df.empty:
        st.info(
            "Sem colunas categóricas disponíveis."
            if not is_en
            else "No categorical columns available."
        )
    else:
        st.dataframe(categories_df, width="stretch")

    st.markdown("**Perfil de Nulos**" if not is_en else "**Null Profile**")
    st.dataframe(null_profile(df), width="stretch")

    st.markdown("**Outliers (IQR)**")
    outliers_df = detect_outliers_iqr(df)
    if outliers_df.empty:
        st.info(
            "Sem colunas numéricas para detecção de outliers."
            if not is_en
            else "No numeric columns available for outlier detection."
        )
    else:
        st.dataframe(outliers_df, width="stretch")

    st.markdown("**Matriz de Correlação**" if not is_en else "**Correlation Matrix**")
    corr_df = correlation_matrix(df)
    if corr_df.empty:
        st.info(
            "Sem colunas numéricas para correlação."
            if not is_en
            else "No numeric columns available for correlation."
        )
    else:
        fig = px.imshow(
            corr_df, text_auto=True, aspect="auto", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("**Statistical Tests**" if is_en else "**Testes Estatísticos**")
    tests_df = run_statistical_tests(df)
    if tests_df.empty:
        st.info(
            "Not enough numeric data for statistical tests."
            if is_en
            else "Dados numéricos insuficientes para testes estatísticos."
        )
    else:
        st.dataframe(tests_df, width="stretch")


def _render_column_analysis(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US

    column = st.selectbox(
        "Selecione a coluna" if not is_en else "Select column",
        options=list(df.columns),
        key="eda_column_selector",
    )
    if column is None:
        return

    series = df[column].dropna()
    null_count = int(df[column].isna().sum())
    null_pct = round(df[column].isna().mean() * 100, 1)
    distinct = int(df[column].nunique(dropna=False))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Linhas" if not is_en else "Rows", len(df))
    m2.metric("Nulos" if not is_en else "Nulls", f"{null_count} ({null_pct}%)")
    m3.metric("Distintos" if not is_en else "Distinct", distinct)
    m4.metric("Dtype", str(df[column].dtype))

    is_numeric = pd.api.types.is_numeric_dtype(df[column])
    is_datetime = pd.api.types.is_datetime64_any_dtype(df[column])

    if is_numeric:
        tab_hist, tab_box = st.tabs(["Histograma / Histogram", "Boxplot"])
        with tab_hist:
            fig_hist = px.histogram(
                df,
                x=column,
                nbins=40,
                title=f"{'Distribuição de' if not is_en else 'Distribution of'} {column}",
                marginal="rug",
            )
            fig_hist.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_hist, use_container_width=True)
        with tab_box:
            fig_box = px.box(
                df,
                y=column,
                title=f"Boxplot — {column}",
                points="outliers",
            )
            fig_box.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_box, use_container_width=True)

        st.markdown(
            "**Resumo Estatístico**" if not is_en else "**Statistical Summary**"
        )
        st.dataframe(
            series.describe().rename("valor" if not is_en else "value").to_frame(),
            width="stretch",
        )

    elif is_datetime:
        fig_ts = px.histogram(
            df,
            x=column,
            title=f"{'Distribuição temporal de' if not is_en else 'Temporal distribution of'} {column}",
        )
        fig_ts.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_ts, use_container_width=True)

    else:
        top_n = st.slider(
            "Top N valores" if not is_en else "Top N values",
            min_value=5,
            max_value=min(50, distinct),
            value=min(20, distinct),
            key="eda_top_n",
        )
        counts = series.value_counts().head(top_n).reset_index()
        counts.columns = [column, "count"]
        fig_bar = px.bar(
            counts,
            x=column,
            y="count",
            title=f"Top {top_n} {'valores de' if not is_en else 'values of'} {column}",
            color="count",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown(
            f"**Top {top_n} valores mais frequentes**"
            if not is_en
            else f"**Top {top_n} most frequent values**"
        )
        st.dataframe(counts, width="stretch")


def render_eda(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader(
        "Exploratory Data Analysis" if is_en else "Análise Exploratória de Dados"
    )

    tab_overview, tab_column = st.tabs(
        ["Visão Geral / Overview", "Análise por Coluna / Column Analysis"]
    )
    with tab_overview:
        _render_overview(df, locale)
    with tab_column:
        _render_column_analysis(df, locale)
