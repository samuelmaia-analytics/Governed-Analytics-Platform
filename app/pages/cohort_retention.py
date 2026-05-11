from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale

COHORT_SLICE_PATH = Path("data/published/semantic/cohort_slice.csv")


def _load_cohort_slice() -> pd.DataFrame:
    if not COHORT_SLICE_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(COHORT_SLICE_PATH)


def render_cohort_retention(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader("Cohort Retention")

    cohort_df = _load_cohort_slice()
    required = {
        "purchase_cohort_month",
        "cohort_order_month_number",
        "customers",
        "avg_ticket",
    }
    if cohort_df.empty or not required.issubset(cohort_df.columns):
        st.info(
            "Slice de cohort indisponível. Execute `python -m src.semantic_layer`."
            if not is_en
            else "Cohort slice unavailable. Run `python -m src.semantic_layer`."
        )
        return

    cohort_df = cohort_df.copy()
    cohort_df["purchase_cohort_month"] = cohort_df["purchase_cohort_month"].astype(str)
    cohort_df["cohort_order_month_number"] = pd.to_numeric(
        cohort_df["cohort_order_month_number"], errors="coerce"
    ).fillna(0)

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
        title="Matriz de Retenção por Cohort (%)"
        if not is_en
        else "Cohort Retention Matrix (%)",
    )
    st.plotly_chart(fig_retention, use_container_width=True)

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
        title="Ticket Médio por Cohort"
        if not is_en
        else "Average Ticket by Cohort",
    )
    st.plotly_chart(fig_ticket, use_container_width=True)

    st.dataframe(
        retention[
            [
                "purchase_cohort_month",
                "cohort_order_month_number",
                "customers",
                "retention_rate",
                "avg_ticket",
            ]
        ].sort_values(["purchase_cohort_month", "cohort_order_month_number"]),
        width="stretch",
    )
