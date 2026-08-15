from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale

CATEGORY_SLICE_PATH = Path("data/published/semantic/category_slice.csv")
COHORT_SLICE_PATH = Path("data/published/semantic/cohort_slice.csv")


def _load_semantic_slice(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _format_brl(value: float) -> str:
    formatted = f"{value:,.2f}"
    return f"R$ {formatted.replace(',', '_').replace('.', ',').replace('_', '.')}"


def _render_executive_kpis(df: pd.DataFrame) -> None:
    revenue = (
        float(pd.to_numeric(df["total_item_value"], errors="coerce").sum())
        if "total_item_value" in df.columns
        else None
    )
    order_count = (
        int(df["order_id"].nunique(dropna=True)) if "order_id" in df.columns else None
    )
    average_ticket = (
        revenue / order_count
        if revenue is not None and order_count is not None and order_count > 0
        else None
    )
    active_sellers = (
        int(df["seller_key"].nunique(dropna=True))
        if "seller_key" in df.columns
        else None
    )

    revenue_col, orders_col, ticket_col, sellers_col = st.columns(4)
    revenue_col.metric(
        "Receita total", _format_brl(revenue) if revenue is not None else "Não disponível"
    )
    orders_col.metric(
        "Pedidos", f"{order_count:,}" if order_count is not None else "Não disponível"
    )
    ticket_col.metric(
        "Ticket médio",
        _format_brl(average_ticket)
        if average_ticket is not None
        else "Não disponível",
    )
    sellers_col.metric(
        "Sellers ativos",
        f"{active_sellers:,}" if active_sellers is not None else "Não disponível",
    )

    st.markdown("### Leitura executiva")
    if (
        revenue is not None
        and order_count is not None
        and average_ticket is not None
        and active_sellers is not None
    ):
        st.markdown(
            f"- A base analisada reúne **{_format_brl(revenue)}** em receita, "
            f"distribuída entre **{order_count:,} pedidos** e "
            f"**{active_sellers:,} sellers ativos**.\n"
            f"- O ticket médio observado no período é de "
            f"**{_format_brl(average_ticket)}**.\n"
            "- As análises abaixo detalham evolução temporal, concentração por "
            "categoria, cohorts e contribuição dos sellers."
        )
    else:
        st.markdown(
            "- As análises abaixo detalham evolução temporal da receita, "
            "concentração por categoria, comportamento por cohort e desempenho "
            "dos sellers."
        )


def _render_monthly_revenue(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    if "total_item_value" not in df.columns:
        st.info(
            "Colunas necessárias não encontradas para série temporal."
            if not is_en
            else "Required columns for time series were not found."
        )
        return

    working_df = df.copy()
    if "order_year_month" not in working_df.columns:
        if {"order_year", "order_month"}.issubset(working_df.columns):
            year = pd.to_numeric(working_df["order_year"], errors="coerce")
            month = pd.to_numeric(working_df["order_month"], errors="coerce")
            working_df["order_year_month"] = (
                year.fillna(0).astype(int).astype(str)
                + "-"
                + month.fillna(0).astype(int).astype(str).str.zfill(2)
            )
        elif "order_purchase_timestamp" in working_df.columns:
            ts = pd.to_datetime(working_df["order_purchase_timestamp"], errors="coerce")
            working_df["order_year_month"] = ts.dt.to_period("M").astype(str)
        else:
            st.info(
                "Colunas temporais necessárias não encontradas para série mensal."
                if not is_en
                else "Temporal columns required for monthly trend were not found."
            )
            return

    monthly = (
        working_df.groupby("order_year_month", dropna=False)["total_item_value"]
        .sum()
        .reset_index()
    )
    monthly = monthly.rename(columns={"total_item_value": "revenue"})
    monthly = monthly.sort_values("order_year_month")
    st.subheader("Evolução mensal da receita")
    st.caption(
        "Permite visualizar crescimento, sazonalidade e mudanças de nível de "
        "receita ao longo do período."
    )
    fig = px.bar(
        monthly,
        x="order_year_month",
        y="revenue",
        title="Evolução mensal da receita",
        labels={
            "order_year_month": "Ano-mês",
            "revenue": "Receita",
        },
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, width="stretch")


def _render_category_pareto(category_slice: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    if category_slice.empty or not {
        "product_category_name_english",
        "revenue",
    }.issubset(category_slice.columns):
        st.info(
            "Slice de categoria indisponível."
            if not is_en
            else "Category slice unavailable."
        )
        return

    category = (
        category_slice.groupby("product_category_name_english", dropna=False)["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    category["category"] = category["product_category_name_english"].fillna("unknown")
    total_revenue = float(category["revenue"].sum())
    if total_revenue > 0:
        category["cum_pct"] = (category["revenue"].cumsum() / total_revenue) * 100
    else:
        category["cum_pct"] = 0.0

    pareto_cutoff = int((category["cum_pct"] <= 80).sum())
    pareto_cutoff = max(1, pareto_cutoff)

    st.subheader("Concentração de receita por categoria")
    fig = px.bar(
        category.head(15),
        x="category",
        y="revenue",
        title="Concentração de receita por categoria",
        labels={"category": "Categoria", "revenue": "Receita"},
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-35)
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"As principais {pareto_cutoff} categorias concentram aproximadamente "
        "80% da receita."
    )
    display_category = category[["category", "revenue", "cum_pct"]].rename(
        columns={
            "category": "Categoria",
            "revenue": "Receita",
            "cum_pct": "Cumulativo %",
        }
    )
    display_category["Receita"] = display_category["Receita"].map(_format_brl)
    st.dataframe(
        display_category,
        width="stretch",
    )


def _render_cohort_ticket_and_retention(
    cohort_slice: pd.DataFrame, locale: Locale
) -> None:
    is_en = locale == LOCALE_EN_US
    required = {
        "purchase_cohort_month",
        "cohort_order_month_number",
        "customers",
        "avg_ticket",
    }
    if cohort_slice.empty or not required.issubset(cohort_slice.columns):
        st.info(
            "Slice de cohort indisponível."
            if not is_en
            else "Cohort slice unavailable."
        )
        return

    cohort_df = cohort_slice.copy()
    cohort_df["purchase_cohort_month"] = cohort_df["purchase_cohort_month"].astype(str)
    cohort_df["cohort_order_month_number"] = pd.to_numeric(
        cohort_df["cohort_order_month_number"], errors="coerce"
    ).fillna(0)

    st.caption(
        "A análise de cohort mostra como ticket médio e retenção evoluem ao "
        "longo dos meses após a primeira compra."
    )

    ticket_pivot = cohort_df.pivot_table(
        index="purchase_cohort_month",
        columns="cohort_order_month_number",
        values="avg_ticket",
        aggfunc="mean",
    )
    fig_ticket = px.imshow(
        ticket_pivot,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Blues",
        title="Ticket médio por cohort",
        labels={
            "x": "Meses desde a primeira compra",
            "y": "Cohort de aquisição",
            "color": "Ticket médio",
        },
    )
    st.plotly_chart(fig_ticket, width="stretch")

    baseline = cohort_df[cohort_df["cohort_order_month_number"] == 0][
        ["purchase_cohort_month", "customers"]
    ].rename(columns={"customers": "baseline_customers"})
    retention = cohort_df.merge(baseline, on="purchase_cohort_month", how="left")
    retention["retention_rate"] = (
        retention["customers"] / retention["baseline_customers"].replace(0, pd.NA)
    ) * 100
    retention_pivot = retention.pivot_table(
        index="purchase_cohort_month",
        columns="cohort_order_month_number",
        values="retention_rate",
        aggfunc="mean",
    )
    fig_retention = px.imshow(
        retention_pivot,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Teal",
        title="Retenção por cohort (%)",
        labels={
            "x": "Meses desde a primeira compra",
            "y": "Cohort de aquisição",
            "color": "Retenção (%)",
        },
    )
    st.plotly_chart(fig_retention, width="stretch")


def _render_top_sellers(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    if not {"seller_key", "total_item_value"}.issubset(df.columns):
        st.info(
            "Colunas de seller não encontradas."
            if not is_en
            else "Seller columns not found."
        )
        return
    sellers = (
        df.groupby("seller_key", dropna=False)["total_item_value"]
        .sum()
        .reset_index()
        .sort_values("total_item_value", ascending=False)
        .head(15)
    )
    st.subheader("Top sellers por receita")
    st.caption(
        "Ranking dos sellers com maior contribuição para a receita no período "
        "analisado."
    )
    fig = px.bar(
        sellers,
        x="seller_key",
        y="total_item_value",
        title="Top sellers por receita",
        labels={
            "seller_key": "Seller",
            "total_item_value": "Receita",
        },
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-35)
    st.plotly_chart(fig, width="stretch")


def render_revenue_analytics(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.title("Business Insights")
    st.markdown(
        "Visão executiva de receita, concentração por categoria, comportamento "
        "de clientes e desempenho de sellers."
    )
    st.caption(
        "Os indicadores apresentados são derivados do dataset demonstrativo "
        "utilizado no projeto de portfólio."
    )
    _render_executive_kpis(df)

    category_slice = _load_semantic_slice(CATEGORY_SLICE_PATH)
    cohort_slice = _load_semantic_slice(COHORT_SLICE_PATH)

    tab_evolution, tab_pareto, tab_cohort, tab_sellers = st.tabs(
        [
            "Evolução da receita",
            "Pareto por categoria",
            "Cohort",
            "Top Sellers",
        ]
    )
    with tab_evolution:
        _render_monthly_revenue(df, locale)
    with tab_pareto:
        _render_category_pareto(category_slice, locale)
    with tab_cohort:
        _render_cohort_ticket_and_retention(cohort_slice, locale)
    with tab_sellers:
        _render_top_sellers(df, locale)

    if category_slice.empty or cohort_slice.empty:
        st.caption(
            "Execute `python -m src.semantic_layer` para materializar os slices semânticos."
            if not is_en
            else "Run `python -m src.semantic_layer` to materialize semantic slices."
        )
