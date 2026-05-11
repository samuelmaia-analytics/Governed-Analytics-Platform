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
    fig = px.bar(
        monthly,
        x="order_year_month",
        y="revenue",
        title="Evolução Mensal da Receita" if not is_en else "Monthly Revenue Evolution",
        labels={"order_year_month": "Ano-Mês" if not is_en else "Year-Month", "revenue": "Receita" if not is_en else "Revenue"},
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)


def _render_category_pareto(category_slice: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    if category_slice.empty or not {"product_category_name_english", "revenue"}.issubset(
        category_slice.columns
    ):
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

    fig = px.bar(
        category.head(15),
        x="category",
        y="revenue",
        title="Pareto de Receita por Categoria (Top 15)"
        if not is_en
        else "Revenue Pareto by Category (Top 15)",
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"As top {pareto_cutoff} categorias concentram ~80% da receita."
        if not is_en
        else f"Top {pareto_cutoff} categories account for ~80% of revenue."
    )
    st.dataframe(
        category[["category", "revenue", "cum_pct"]]
        .rename(columns={"category": "Categoria" if not is_en else "Category", "revenue": "Receita" if not is_en else "Revenue", "cum_pct": "Cumulativo %" if not is_en else "Cumulative %"}),
        width="stretch",
    )


def _render_cohort_ticket_and_retention(cohort_slice: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    required = {"purchase_cohort_month", "cohort_order_month_number", "customers", "avg_ticket"}
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
        title="Ticket Médio por Cohort (Heatmap)"
        if not is_en
        else "Average Ticket by Cohort (Heatmap)",
    )
    st.plotly_chart(fig_ticket, use_container_width=True)

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
        title="Retenção por Cohort (%)" if not is_en else "Cohort Retention (%)",
    )
    st.plotly_chart(fig_retention, use_container_width=True)


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
    fig = px.bar(
        sellers,
        x="seller_key",
        y="total_item_value",
        title="Top Sellers por Receita" if not is_en else "Top Sellers by Revenue",
        labels={"seller_key": "Seller", "total_item_value": "Receita" if not is_en else "Revenue"},
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)


def render_revenue_analytics(df: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader("Revenue Analytics")

    category_slice = _load_semantic_slice(CATEGORY_SLICE_PATH)
    cohort_slice = _load_semantic_slice(COHORT_SLICE_PATH)

    tab_evolution, tab_pareto, tab_cohort, tab_sellers = st.tabs(
        ["Evolução / Evolution", "Pareto Categorias / Category Pareto", "Cohort", "Top Sellers"]
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
