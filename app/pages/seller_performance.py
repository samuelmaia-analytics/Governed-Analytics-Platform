from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale

SELLER_SLICE_PATH = Path("data/published/semantic/seller_slice.csv")


def _load_seller_slice() -> pd.DataFrame:
    if not SELLER_SLICE_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(SELLER_SLICE_PATH)


def render_seller_performance(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader("Seller Performance")

    seller_df = _load_seller_slice()
    if seller_df.empty:
        st.info(
            "Seller slice indisponível. Execute `python -m src.semantic_layer`."
            if not is_en
            else "Seller slice unavailable. Run `python -m src.semantic_layer`."
        )
        return

    tier_options = ["all"] + sorted(
        str(value) for value in seller_df["seller_volume_tier"].dropna().unique()
    )
    state_options = ["all"] + sorted(
        str(value) for value in seller_df["seller_state"].dropna().unique()
    )

    f1, f2 = st.columns(2)
    selected_tier = f1.selectbox(
        "Tier de Volume" if not is_en else "Volume Tier",
        options=tier_options,
        key="seller_perf_tier_filter",
    )
    selected_state = f2.selectbox(
        "Estado do Seller" if not is_en else "Seller State",
        options=state_options,
        key="seller_perf_state_filter",
    )

    filtered = seller_df.copy()
    if selected_tier != "all":
        filtered = filtered[filtered["seller_volume_tier"] == selected_tier]
    if selected_state != "all":
        filtered = filtered[filtered["seller_state"] == selected_state]

    if filtered.empty:
        st.warning(
            "Nenhum seller encontrado para os filtros selecionados."
            if not is_en
            else "No sellers found for selected filters."
        )
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sellers", int(filtered["seller_key"].nunique()))
    m2.metric(
        "Orders",
        int(pd.to_numeric(filtered["seller_order_count"], errors="coerce").fillna(0).sum()),
    )
    m3.metric(
        "Avg Delay Rate",
        f"{(pd.to_numeric(filtered['delay_rate'], errors='coerce').mean() * 100):.1f}%",
    )
    m4.metric(
        "Avg Delivery (days)",
        f"{pd.to_numeric(filtered['avg_delivery_time_days'], errors='coerce').mean():.1f}",
    )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        tier_dist = (
            filtered["seller_volume_tier"]
            .astype(str)
            .value_counts()
            .rename_axis("seller_volume_tier")
            .reset_index(name="count")
        )
        fig_tier = px.bar(
            tier_dist,
            x="seller_volume_tier",
            y="count",
            color="seller_volume_tier",
            title="Distribuição por Tier" if not is_en else "Tier Distribution",
        )
        fig_tier.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_tier, use_container_width=True)

    with chart_right:
        sla = (
            filtered.groupby("seller_volume_tier", dropna=False)
            .agg(
                avg_delay_rate=("delay_rate", "mean"),
                avg_delivery_days=("avg_delivery_time_days", "mean"),
            )
            .reset_index()
        )
        sla["avg_delay_rate"] = sla["avg_delay_rate"] * 100
        fig_sla = px.bar(
            sla,
            x="seller_volume_tier",
            y="avg_delay_rate",
            color="avg_delay_rate",
            title="SLA de Atraso por Tier (%)"
            if not is_en
            else "Delay SLA by Tier (%)",
            labels={"avg_delay_rate": "Delay Rate (%)"},
        )
        fig_sla.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sla, use_container_width=True)

    ranking = filtered.copy()
    ranking["estimated_revenue"] = (
        pd.to_numeric(ranking["avg_ticket"], errors="coerce").fillna(0)
        * pd.to_numeric(ranking["seller_order_count"], errors="coerce").fillna(0)
    )
    ranking = ranking.sort_values("estimated_revenue", ascending=False).head(20)

    st.markdown("**Top Sellers (Estimated Revenue)**")
    st.dataframe(
        ranking[
            [
                "seller_key",
                "seller_state",
                "seller_volume_tier",
                "seller_order_count",
                "avg_ticket",
                "estimated_revenue",
                "delay_rate",
                "avg_delivery_time_days",
                "avg_review_score",
            ]
        ],
        width="stretch",
    )
