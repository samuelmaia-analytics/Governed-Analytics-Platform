from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import Locale

SELLER_SLICE_PATH = Path("data/published/semantic/seller_slice.csv")

_TIER_LABELS = {
    "all": "Todos",
    "long_tail": "Cauda longa",
    "scaled": "Em escala",
    "core": "Core",
    "strategic": "Estratégico",
}

_RANKING_COLUMNS = [
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


def _load_seller_slice() -> pd.DataFrame:
    if not SELLER_SLICE_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(SELLER_SLICE_PATH)


def _display_tier(value: object) -> str:
    technical_value = str(value)
    return _TIER_LABELS.get(
        technical_value, technical_value.replace("_", " ").capitalize()
    )


def _display_filter_value(value: object) -> str:
    return "Todos" if str(value) == "all" else str(value)


def _format_integer(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def _format_decimal(value: float, decimal_places: int) -> str:
    formatted = f"{value:,.{decimal_places}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def _format_currency(value: int | float) -> str:
    return f"R$ {_format_decimal(float(value), 2)}"


def _format_percentage(value: int | float) -> str:
    return f"{_format_decimal(float(value) * 100, 1)}%"


def _format_delivery_days(value: int | float) -> str:
    return f"{_format_decimal(float(value), 1)} dias"


def _format_review_score(value: int | float) -> str:
    return _format_decimal(float(value), 2)


def _build_executive_ranking(ranking: pd.DataFrame) -> pd.DataFrame:
    executive = ranking.copy()
    executive["seller_display"] = executive["seller_key"].map(
        lambda value: f"Seller • {str(value)[-8:]}"
    )
    executive["seller_volume_tier"] = executive["seller_volume_tier"].map(
        _display_tier
    )
    executive["avg_ticket"] = executive["avg_ticket"].map(_format_currency)
    executive["estimated_revenue"] = executive["estimated_revenue"].map(
        _format_currency
    )
    executive["delay_rate"] = executive["delay_rate"].map(_format_percentage)
    executive["avg_delivery_time_days"] = executive[
        "avg_delivery_time_days"
    ].map(_format_delivery_days)
    executive["avg_review_score"] = executive["avg_review_score"].map(
        _format_review_score
    )
    return executive[
        [
            "seller_display",
            "seller_state",
            "seller_volume_tier",
            "seller_order_count",
            "avg_ticket",
            "estimated_revenue",
            "delay_rate",
            "avg_delivery_time_days",
            "avg_review_score",
        ]
    ].rename(
        columns={
            "seller_display": "Seller",
            "seller_state": "Estado",
            "seller_volume_tier": "Faixa de volume",
            "seller_order_count": "Pedidos",
            "avg_ticket": "Ticket médio",
            "estimated_revenue": "Receita estimada",
            "delay_rate": "Taxa de atraso",
            "avg_delivery_time_days": "Entrega média",
            "avg_review_score": "Avaliação média",
        }
    )


def render_seller_performance(locale: Locale) -> None:
    del locale
    st.title("Desempenho de Sellers")
    st.markdown(
        "Visão de volume, experiência logística e contribuição estimada dos "
        "sellers no cenário analítico demonstrativo."
    )
    st.caption(
        "Os indicadores combinam pedidos, atraso, tempo de entrega e receita "
        "estimada para apoiar a comparação de desempenho entre sellers."
    )
    st.markdown("### Como interpretar esta página")
    st.write(
        "Use os filtros para comparar grupos de sellers por volume e localização. "
        "Os indicadores ajudam a identificar concentração de pedidos, comportamento "
        "logístico e contribuição estimada."
    )

    seller_df = _load_seller_slice()
    if seller_df.empty:
        st.info("Dados de sellers não disponíveis neste ambiente.")
        st.caption(
            "A visualização depende do slice semântico de sellers gerado em uma "
            "execução controlada."
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
        "Faixa de volume",
        options=tier_options,
        format_func=_display_tier,
        key="seller_perf_tier_filter",
    )
    selected_state = f2.selectbox(
        "Estado",
        options=state_options,
        format_func=_display_filter_value,
        key="seller_perf_state_filter",
    )

    filtered = seller_df.copy()
    if selected_tier != "all":
        filtered = filtered[filtered["seller_volume_tier"] == selected_tier]
    if selected_state != "all":
        filtered = filtered[filtered["seller_state"] == selected_state]

    if filtered.empty:
        st.warning("Nenhum seller encontrado para os filtros selecionados.")
        return

    seller_count = int(filtered["seller_key"].nunique())
    order_count = int(
        pd.to_numeric(filtered["seller_order_count"], errors="coerce")
        .fillna(0)
        .sum()
    )
    avg_delay_rate = (
        float(pd.to_numeric(filtered["delay_rate"], errors="coerce").mean()) * 100
    )
    avg_delivery_days = float(
        pd.to_numeric(filtered["avg_delivery_time_days"], errors="coerce").mean()
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sellers ativos", _format_integer(seller_count))
    m2.metric("Pedidos", _format_integer(order_count))
    m3.metric("Taxa média de atraso", f"{_format_decimal(avg_delay_rate, 1)}%")
    m4.metric(
        "Tempo médio de entrega",
        f"{_format_decimal(avg_delivery_days, 1)} dias",
    )

    st.markdown("### Leitura executiva")
    st.markdown(
        f"- A seleção atual reúne **{_format_integer(seller_count)} sellers** e "
        f"**{_format_integer(order_count)} pedidos**.\n"
        f"- A taxa média de atraso é **{_format_decimal(avg_delay_rate, 1)}%**.\n"
        f"- O tempo médio de entrega é "
        f"**{_format_decimal(avg_delivery_days, 1)} dias**."
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
        display_tier_dist = tier_dist.assign(
            tier_label=tier_dist["seller_volume_tier"].map(_display_tier)
        )
        fig_tier = px.bar(
            display_tier_dist,
            x="count",
            y="tier_label",
            color="tier_label",
            orientation="h",
            title="Distribuição de sellers por faixa de volume",
            labels={
                "count": "Quantidade de sellers",
                "tier_label": "Faixa de volume",
            },
            hover_data={"seller_volume_tier": True, "tier_label": False},
        )
        fig_tier.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_tier, width="stretch")

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
        display_sla = sla.assign(
            tier_label=sla["seller_volume_tier"].map(_display_tier)
        )
        fig_sla = px.bar(
            display_sla,
            x="avg_delay_rate",
            y="tier_label",
            color="avg_delay_rate",
            orientation="h",
            title="Taxa média de atraso por faixa de volume",
            labels={
                "avg_delay_rate": "Taxa média de atraso (%)",
                "tier_label": "Faixa de volume",
            },
            hover_data={"seller_volume_tier": True, "tier_label": False},
        )
        fig_sla.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sla, width="stretch")

    ranking = filtered.copy()
    ranking["estimated_revenue"] = pd.to_numeric(
        ranking["avg_ticket"], errors="coerce"
    ).fillna(0) * pd.to_numeric(ranking["seller_order_count"], errors="coerce").fillna(
        0
    )
    ranking = ranking.sort_values("estimated_revenue", ascending=False).head(20)

    technical_ranking = ranking[_RANKING_COLUMNS].copy()
    executive_ranking = _build_executive_ranking(technical_ranking)

    st.markdown("### Top Sellers por Receita Estimada")
    st.dataframe(
        executive_ranking,
        width="stretch",
        hide_index=True,
    )

    with st.expander("Detalhes técnicos dos sellers", expanded=False):
        st.dataframe(technical_ranking, width="stretch", hide_index=True)
