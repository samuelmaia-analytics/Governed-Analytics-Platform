from __future__ import annotations

import re

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

    def generate_storytelling_insights(df: pd.DataFrame) -> list[str]:
        _ = df
        return []

    def run_statistical_tests(df: pd.DataFrame) -> pd.DataFrame:
        _ = df
        return pd.DataFrame()


_DESCRIPTIVE_LABELS_PT = {
    "count": "Contagem",
    "unique": "Únicos",
    "top": "Mais frequente",
    "freq": "Frequência",
    "mean": "Média",
    "std": "Desvio padrão",
    "min": "Mínimo",
    "25%": "25%",
    "50%": "Mediana",
    "75%": "75%",
    "max": "Máximo",
}

_DTYPE_LABELS_PT = {
    "object": "Texto / categórico",
    "float64": "Decimal",
    "int64": "Inteiro",
    "bool": "Booleano",
}

_TEST_LABELS_PT = {
    "jarque_bera_normality": "Normalidade — Jarque-Bera",
    "pearson_correlation_significance": (
        "Significância da correlação de Pearson"
    ),
}

_INTERPRETATION_LABELS_PT = {
    "non_normal": "Distribuição com evidência de não normalidade",
    "cannot_reject_normality": (
        "Sem evidência suficiente para rejeitar normalidade"
    ),
    "significant_correlation": "Correlação estatisticamente significativa",
    "weak_evidence": "Evidência estatística fraca",
}


def _format_decimal(value: int | float, decimal_places: int) -> str:
    formatted = f"{float(value):,.{decimal_places}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def _format_integer(value: int | float) -> str:
    return f"{int(float(value)):,}".replace(",", ".")


def _format_percentage(value: int | float, decimal_places: int = 2) -> str:
    return f"{_format_decimal(value, decimal_places)}%"


def _translate_known_insight(insight: str, locale: Locale) -> str | None:
    if locale == LOCALE_EN_US:
        return insight

    null_match = re.fullmatch(
        r"Highest null concentration is `(.+)` with ([\d.]+)% missing values\.",
        insight,
    )
    if null_match:
        column, percentage = null_match.groups()
        return (
            f"A maior concentração de valores ausentes está em `{column}`, com "
            f"{percentage.replace('.', ',')}%."
        )

    category_match = re.fullmatch(
        r"Top category concentration: `(.+)` = `(.+)` with (\d+) rows "
        r"\(([\d.]+)%\)\.",
        insight,
    )
    if category_match:
        column, category, count, percentage = category_match.groups()
        return (
            f"A maior concentração categórica está em `{column}` = `{category}`, "
            f"com {_format_integer(int(count))} registros "
            f"({percentage.replace('.', ',')}%)."
        )

    outlier_match = re.fullmatch(
        r"Strongest outlier signal appears in `(.+)` "
        r"\(([\d.]+)% rows outside IQR bounds\)\.",
        insight,
    )
    if outlier_match:
        column, percentage = outlier_match.groups()
        return (
            f"O maior sinal de outliers aparece em `{column}`, com "
            f"{percentage.replace('.', ',')}% dos registros fora dos limites IQR."
        )

    correlation_match = re.fullmatch(
        r"Highest numeric correlation is between `(.+)` and `(.+)` "
        r"\(\|r\|=([\d.]+)\)\.",
        insight,
    )
    if correlation_match:
        column_x, column_y, correlation = correlation_match.groups()
        return (
            f"A maior correlação numérica ocorre entre `{column_x}` e "
            f"`{column_y}` (|r|={correlation.replace('.', ',')})."
        )

    return None


def _render_narrative_insights(insights: list[str], locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.markdown("**Narrative Insights**" if is_en else "**Insights narrativos**")
    if not insights:
        st.info(
            "No narrative insights available for this dataset."
            if is_en
            else "Sem insights narrativos disponíveis para este dataset."
        )
        return

    rendered_insight = False
    for insight in insights:
        translated = _translate_known_insight(insight, locale)
        if translated is not None:
            st.write(f"- {translated}")
            rendered_insight = True

    if not rendered_insight:
        st.info(
            "Narrative insights are available in the technical details."
            if is_en
            else "Os insights narrativos estão disponíveis nos detalhes técnicos."
        )


def _present_descriptive_statistics(
    descriptive_df: pd.DataFrame, locale: Locale
) -> pd.DataFrame:
    presentation = descriptive_df.copy()
    presentation.index.name = "Variable" if locale == LOCALE_EN_US else "Variável"
    presentation = presentation.reset_index()
    if locale != LOCALE_EN_US:
        presentation = presentation.rename(columns=_DESCRIPTIVE_LABELS_PT)
    return presentation


def _present_dtype_distribution(
    dtype_df: pd.DataFrame, locale: Locale
) -> pd.DataFrame:
    presentation = dtype_df.copy()
    if locale == LOCALE_EN_US:
        return presentation.rename(
            columns={"dtype": "Type", "count": "Columns", "percentage": "Percentage"}
        )

    presentation["dtype"] = presentation["dtype"].map(
        lambda value: _DTYPE_LABELS_PT.get(str(value), str(value))
    )
    presentation["percentage"] = presentation["percentage"].map(_format_percentage)
    return presentation.rename(
        columns={"dtype": "Tipo", "count": "Colunas", "percentage": "Percentual"}
    )


def _present_top_categories(
    categories_df: pd.DataFrame, locale: Locale
) -> pd.DataFrame:
    presentation = categories_df.copy()
    if locale == LOCALE_EN_US:
        return presentation.rename(
            columns={
                "column_name": "Variable",
                "category": "Category",
                "count": "Rows",
                "percentage": "Percentage",
            }
        )

    presentation["percentage"] = presentation["percentage"].map(_format_percentage)
    return presentation.rename(
        columns={
            "column_name": "Variável",
            "category": "Categoria",
            "count": "Registros",
            "percentage": "Percentual",
        }
    )


def _present_null_profile(null_df: pd.DataFrame, locale: Locale) -> pd.DataFrame:
    presentation = null_df.copy()
    if locale == LOCALE_EN_US:
        return presentation.rename(
            columns={
                "column_name": "Variable",
                "null_count": "Missing values",
                "null_pct": "Missing percentage",
            }
        )

    presentation["null_pct"] = presentation["null_pct"].map(_format_percentage)
    return presentation.rename(
        columns={
            "column_name": "Variável",
            "null_count": "Valores ausentes",
            "null_pct": "Percentual ausente",
        }
    )


def _present_outliers(outliers_df: pd.DataFrame, locale: Locale) -> pd.DataFrame:
    presentation = outliers_df.copy()
    if locale == LOCALE_EN_US:
        return presentation.rename(
            columns={
                "column_name": "Variable",
                "lower_bound": "Lower bound",
                "upper_bound": "Upper bound",
                "outlier_count": "Outliers",
                "outlier_pct": "Outlier percentage",
            }
        )

    presentation["outlier_pct"] = presentation["outlier_pct"].map(
        _format_percentage
    )
    return presentation.rename(
        columns={
            "column_name": "Variável",
            "q1": "Q1",
            "q3": "Q3",
            "iqr": "IQR",
            "lower_bound": "Limite inferior",
            "upper_bound": "Limite superior",
            "outlier_count": "Outliers",
            "outlier_pct": "Percentual de outliers",
        }
    )


def _present_statistical_tests(
    tests_df: pd.DataFrame, locale: Locale
) -> pd.DataFrame:
    presentation = tests_df.copy()
    if locale == LOCALE_EN_US:
        return presentation.rename(
            columns={
                "test_name": "Test",
                "target": "Target",
                "statistic": "Statistic",
                "p_value": "p-value",
                "interpretation": "Interpretation",
            }
        )

    presentation["test_name"] = presentation["test_name"].map(
        lambda value: _TEST_LABELS_PT.get(str(value), str(value))
    )
    presentation["interpretation"] = presentation["interpretation"].map(
        lambda value: _INTERPRETATION_LABELS_PT.get(str(value), str(value))
    )
    return presentation.rename(
        columns={
            "test_name": "Teste",
            "target": "Variável",
            "statistic": "Estatística",
            "p_value": "Valor-p",
            "interpretation": "Interpretação",
        }
    )


def _render_overview(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US

    insights = generate_storytelling_insights(df)
    descriptive_df = descriptive_statistics(df)
    dtype_df = dtype_distribution(df)
    categories_df = top_categories(df)
    null_df = null_profile(df)
    outliers_df = detect_outliers_iqr(df)
    corr_df = correlation_matrix(df)
    tests_df = run_statistical_tests(df)

    numeric_columns = int(corr_df.shape[1])
    columns_with_nulls = int((null_df["null_pct"] > 0).sum())

    summary_tab, profile_tab, relations_tab, statistical_tab = st.tabs(
        [
            "Summary" if is_en else "Resumo",
            "Structural profile" if is_en else "Perfil estrutural",
            "Numeric relationships" if is_en else "Relações numéricas",
            "Statistical details" if is_en else "Detalhes estatísticos",
        ]
    )

    with summary_tab:
        metric_1, metric_2, metric_3, metric_4 = st.columns(4)
        metric_1.metric("Rows" if is_en else "Registros", _format_integer(len(df)))
        metric_2.metric(
            "Columns" if is_en else "Colunas", _format_integer(len(df.columns))
        )
        metric_3.metric(
            "Numeric columns" if is_en else "Colunas numéricas",
            _format_integer(numeric_columns),
        )
        metric_4.metric(
            "Columns with missing values" if is_en else "Colunas com nulos",
            _format_integer(columns_with_nulls),
        )

        st.markdown("### Technical reading" if is_en else "### Leitura técnica")
        if is_en:
            st.markdown(
                f"- The current asset has **{_format_integer(len(df))} rows** and "
                f"**{_format_integer(len(df.columns))} columns**.\n"
                f"- **{_format_integer(columns_with_nulls)} columns** contain missing "
                "values.\n"
                f"- Numeric analysis considers **{_format_integer(numeric_columns)} "
                "columns**.\n"
                f"- The correlation matrix contains **{_format_integer(corr_df.shape[1])} "
                "numeric variables**."
            )
        else:
            st.markdown(
                f"- O ativo atual possui **{_format_integer(len(df))} registros** e "
                f"**{_format_integer(len(df.columns))} colunas**.\n"
                f"- **{_format_integer(columns_with_nulls)} colunas** possuem valores "
                "ausentes.\n"
                f"- A análise numérica considera **{_format_integer(numeric_columns)} "
                "colunas**.\n"
                f"- A matriz de correlação contém **{_format_integer(corr_df.shape[1])} "
                "variáveis numéricas**."
            )

        _render_narrative_insights(insights, locale)

    with profile_tab:
        st.markdown(
            "### Descriptive statistics" if is_en else "### Estatísticas descritivas"
        )
        st.dataframe(
            _present_descriptive_statistics(descriptive_df, locale),
            width="stretch",
            hide_index=True,
        )

        st.markdown(
            "### Data type distribution"
            if is_en
            else "### Distribuição dos tipos de dados"
        )
        if not dtype_df.empty:
            dtype_presentation = _present_dtype_distribution(dtype_df, locale)
            type_column = "Type" if is_en else "Tipo"
            count_column = "Columns" if is_en else "Colunas"
            st.bar_chart(dtype_presentation.set_index(type_column)[[count_column]])
            st.dataframe(dtype_presentation, width="stretch", hide_index=True)

        st.markdown(
            "### Most frequent categories"
            if is_en
            else "### Categorias mais frequentes"
        )
        if categories_df.empty:
            st.info(
                "No categorical columns available."
                if is_en
                else "Sem colunas categóricas disponíveis."
            )
        else:
            st.dataframe(
                _present_top_categories(categories_df, locale),
                width="stretch",
                hide_index=True,
            )

        st.markdown(
            "### Missing values profile"
            if is_en
            else "### Perfil de valores ausentes"
        )
        st.dataframe(
            _present_null_profile(null_df, locale),
            width="stretch",
            hide_index=True,
        )

        st.markdown(
            "### Outliers using the IQR method"
            if is_en
            else "### Outliers pelo método IQR"
        )
        st.caption(
            "The IQR method flags values outside limits defined by 1.5 × the "
            "interquartile range. These points warrant investigation and are not "
            "automatically errors."
            if is_en
            else "O método IQR sinaliza valores fora dos limites definidos por 1,5 × "
            "intervalo interquartil. Isso indica pontos para investigação e não "
            "significa automaticamente erro."
        )
        if outliers_df.empty:
            st.info(
                "No numeric columns available for outlier detection."
                if is_en
                else "Sem colunas numéricas para detecção de outliers."
            )
        else:
            st.dataframe(
                _present_outliers(outliers_df, locale),
                width="stretch",
                hide_index=True,
            )

    with relations_tab:
        st.markdown(
            "### Correlation matrix between numeric variables"
            if is_en
            else "### Matriz de correlação entre variáveis numéricas"
        )
        st.caption(
            "Correlation measures linear association. Values close to +1 or -1 "
            "indicate stronger association; correlation does not imply causation."
            if is_en
            else "Correlação mede associação linear. Valores próximos de +1 ou -1 "
            "indicam associação mais forte; correlação não implica causalidade."
        )
        if corr_df.empty:
            st.info(
                "No numeric columns available for correlation."
                if is_en
                else "Sem colunas numéricas para correlação."
            )
        else:
            fig = px.imshow(
                corr_df, text_auto=True, aspect="auto", color_continuous_scale="Blues"
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, width="stretch")

    with statistical_tab:
        st.markdown("### Statistical tests" if is_en else "### Testes estatísticos")
        st.caption(
            "The tests help assess statistical properties of the variables. The "
            "significance threshold remains 0.05."
            if is_en
            else "Os testes apresentados ajudam a avaliar propriedades estatísticas "
            "das variáveis. O limiar de significância utilizado permanece 0,05."
        )
        if tests_df.empty:
            st.info(
                "Not enough numeric data for statistical tests."
                if is_en
                else "Dados numéricos insuficientes para testes estatísticos."
            )
        else:
            st.dataframe(
                _present_statistical_tests(tests_df, locale),
                width="stretch",
                hide_index=True,
            )

    with st.expander(
        "Technical analysis details" if is_en else "Detalhes técnicos da análise",
        expanded=False,
    ):
        st.caption(
            "The tables below preserve the original helper outputs, technical names, "
            "enums, and numeric values."
            if is_en
            else "As tabelas abaixo preservam os outputs originais dos helpers, "
            "nomes técnicos, enums e valores numéricos."
        )
        if insights:
            st.markdown(
                "**Original narrative insights**"
                if is_en
                else "**Insights narrativos originais**"
            )
            for insight in insights:
                st.write(f"- {insight}")
        st.markdown("**descriptive_statistics**")
        st.dataframe(descriptive_df, width="stretch")
        st.markdown("**dtype_distribution**")
        st.dataframe(dtype_df, width="stretch", hide_index=True)
        st.markdown("**top_categories**")
        st.dataframe(categories_df, width="stretch", hide_index=True)
        st.markdown("**null_profile**")
        st.dataframe(null_df, width="stretch", hide_index=True)
        st.markdown("**detect_outliers_iqr**")
        st.dataframe(outliers_df, width="stretch", hide_index=True)
        st.markdown("**correlation_matrix**")
        st.dataframe(corr_df, width="stretch")
        st.markdown("**run_statistical_tests**")
        st.dataframe(tests_df, width="stretch", hide_index=True)


def _render_column_analysis(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US

    st.markdown(
        "### Detailed column analysis"
        if is_en
        else "### Análise detalhada por coluna"
    )
    st.caption(
        "Select a variable to inspect missing values, cardinality, and distribution."
        if is_en
        else "Selecione uma variável para inspecionar valores ausentes, "
        "cardinalidade e distribuição."
    )
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
    m4.metric("Tipo" if not is_en else "Type", str(df[column].dtype))

    is_numeric = pd.api.types.is_numeric_dtype(df[column])
    is_datetime = pd.api.types.is_datetime64_any_dtype(df[column])

    if is_numeric:
        tab_hist, tab_box = st.tabs(
            ["Distribution" if is_en else "Distribuição", "Boxplot"]
        )
        with tab_hist:
            fig_hist = px.histogram(
                df,
                x=column,
                nbins=40,
                title=f"{'Distribuição de' if not is_en else 'Distribution of'} {column}",
                marginal="rug",
            )
            fig_hist.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_hist, width="stretch")
        with tab_box:
            fig_box = px.box(
                df,
                y=column,
                title=f"Boxplot — {column}",
                points="outliers",
            )
            fig_box.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_box, width="stretch")

        st.markdown(
            "### Statistical summary" if is_en else "### Resumo estatístico"
        )
        summary_df = (
            series.describe().rename("valor" if not is_en else "value").to_frame()
        )
        summary_df.index.name = "Estatística" if not is_en else "Statistic"
        st.dataframe(summary_df.reset_index(), width="stretch", hide_index=True)

    elif is_datetime:
        fig_ts = px.histogram(
            df,
            x=column,
            title=f"{'Distribuição temporal de' if not is_en else 'Temporal distribution of'} {column}",
        )
        fig_ts.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_ts, width="stretch")

    else:
        top_n = st.slider(
            "Quantidade de categorias exibidas"
            if not is_en
            else "Number of categories displayed",
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
            title=(
                f"Top {top_n} categorias mais frequentes de {column}"
                if not is_en
                else f"Top {top_n} most frequent categories of {column}"
            ),
            color="count",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
        st.plotly_chart(fig_bar, width="stretch")

        st.markdown(
            f"### Top {top_n} categorias mais frequentes"
            if not is_en
            else f"### Top {top_n} most frequent categories"
        )
        presentation_counts = counts.rename(
            columns={
                column: "Categoria" if not is_en else "Category",
                "count": "Frequência" if not is_en else "Frequency",
            }
        )
        st.dataframe(presentation_counts, width="stretch", hide_index=True)


def render_eda(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.title("Technical Data Analysis" if is_en else "Análise Técnica dos Dados")
    st.subheader(
        "Exploratory diagnosis of the analytical asset to understand structure, "
        "distribution, missing values, outliers, and relationships between variables."
        if is_en
        else "Diagnóstico exploratório do ativo analítico para compreender estrutura, "
        "distribuição, ausência de valores, outliers e relações entre variáveis."
    )
    st.caption(
        "This page presents a technical view of the current dataset. The results "
        "support data investigation and understanding, but do not, by themselves, "
        "represent business decisions or causality."
        if is_en
        else "Esta página apresenta uma visão técnica do dataset atual. Os resultados "
        "apoiam investigação e entendimento dos dados, mas não representam, por si "
        "só, decisões de negócio ou causalidade."
    )
    st.markdown(
        "### How to interpret this page"
        if is_en
        else "### Como interpretar esta página"
    )
    st.write(
        "The analysis combines structural profiling, descriptive statistics, "
        "distributions, missing values, outliers, correlations, and statistical "
        "tests. Each result should be interpreted in the context of the data."
        if is_en
        else "A análise combina perfil estrutural, estatísticas descritivas, "
        "distribuições, valores ausentes, outliers, correlações e testes estatísticos. "
        "Cada resultado deve ser interpretado no contexto do dado analisado."
    )

    tab_overview, tab_column = st.tabs(
        [
            "Overview" if is_en else "Visão Geral",
            "Column Analysis" if is_en else "Análise por Coluna",
        ]
    )
    with tab_overview:
        _render_overview(df, locale)
    with tab_column:
        _render_column_analysis(df, locale)
