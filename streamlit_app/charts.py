from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from streamlit_app.analytics import build_state_table, to_order_level
from streamlit_app.theme import APP_FONT, COLORS, MONTH_NAME_MAP, WEEKDAY_MAP


def base_layout(fig: go.Figure, *, show_legend: bool = False) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font=dict(family=APP_FONT, size=13, color=COLORS["text"]),
        title_font=dict(size=18, color=COLORS["text"]),
        margin=dict(l=24, r=20, t=86, b=24),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(size=12, color=COLORS["text"]),
            bgcolor="rgba(255,255,255,0.96)",
            bordercolor=COLORS["border"],
            borderwidth=1,
        ),
        showlegend=show_legend,
        hoverlabel=dict(bgcolor=COLORS["surface"], bordercolor=COLORS["border"], font=dict(family=APP_FONT, color=COLORS["text"])),
        height=375,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color=COLORS["muted"]), title_font=dict(color=COLORS["text"]))
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, tickfont=dict(color=COLORS["muted"]), title_font=dict(color=COLORS["text"]))
    return fig


def chart_revenue_line(df: pd.DataFrame) -> go.Figure:
    timeline = df.groupby("month_start", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("month_start")
    fig = px.line(timeline, x="month_start", y="revenue", title="Como a receita evolui ao longo do tempo", labels={"month_start": "Período", "revenue": "Receita"})
    fig.update_traces(line=dict(color=COLORS["primary"], width=3.5), marker=dict(size=7))
    return base_layout(fig)


def chart_orders_area(df: pd.DataFrame) -> go.Figure:
    timeline = df.groupby("month_start", as_index=False).agg(orders=("order_id", "nunique")).sort_values("month_start")
    fig = px.area(timeline, x="month_start", y="orders", title="Como o volume de pedidos varia no tempo", labels={"month_start": "Período", "orders": "Pedidos"})
    fig.update_traces(line=dict(color=COLORS["secondary"], width=2.8), fillcolor="rgba(59, 130, 246, 0.16)")
    return base_layout(fig)


def chart_seasonality_heatmap(df: pd.DataFrame) -> go.Figure:
    heatmap_df = (
        df.assign(month_num=df["order_purchase_timestamp"].dt.month, weekday_num=df["order_purchase_timestamp"].dt.weekday)
        .groupby(["weekday_num", "month_num"], as_index=False)
        .agg(revenue=("total_item_value", "sum"))
    )
    pivot_df = heatmap_df.pivot(index="weekday_num", columns="month_num", values="revenue").reindex(index=range(7), columns=range(1, 13)).fillna(0)
    fig = px.imshow(
        pivot_df,
        x=[MONTH_NAME_MAP[idx] for idx in pivot_df.columns],
        y=[WEEKDAY_MAP[idx] for idx in pivot_df.index],
        color_continuous_scale=[[0, "#EFF6FF"], [0.5, "#93C5FD"], [1, "#1D4ED8"]],
        title="Sazonalidade de receita por mês e dia da semana",
        labels=dict(x="Mês", y="Dia da semana", color="Receita"),
        aspect="auto",
    )
    fig.update_layout(height=405)
    return base_layout(fig)


def chart_delay_by_period(df: pd.DataFrame) -> go.Figure:
    delivered = to_order_level(df)
    delivered = delivered[delivered["order_delivered_customer_date"].notna()].copy()
    period_df = delivered.groupby("quarter_label", as_index=False).agg(delay_rate=("is_delayed", "mean")).sort_values("quarter_label")
    period_df["delay_rate"] = period_df["delay_rate"] * 100
    fig = px.bar(period_df, x="quarter_label", y="delay_rate", title="Quais períodos concentram pior desempenho operacional", labels={"quarter_label": "Trimestre", "delay_rate": "Taxa de atraso (%)"}, color_discrete_sequence=[COLORS["highlight"]])
    return base_layout(fig)


def chart_top_categories_revenue(df: pd.DataFrame) -> go.Figure:
    category_df = df.groupby("category_label", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("revenue", ascending=False).head(12).sort_values("revenue")
    fig = px.bar(category_df, x="revenue", y="category_label", orientation="h", title="Quais categorias mais faturam", labels={"category_label": "Categoria", "revenue": "Receita"}, color_discrete_sequence=[COLORS["primary"]])
    return base_layout(fig)


def chart_top_categories_orders(df: pd.DataFrame) -> go.Figure:
    category_df = df.groupby("category_label", as_index=False).agg(orders=("order_id", "nunique")).sort_values("orders", ascending=False).head(10)
    fig = px.bar(category_df, x="category_label", y="orders", title="Quais categorias mais vendem", labels={"category_label": "Categoria", "orders": "Pedidos"}, color_discrete_sequence=[COLORS["secondary"]])
    fig.update_xaxes(tickangle=-28)
    return base_layout(fig)


def chart_category_share_donut(df: pd.DataFrame) -> go.Figure:
    category_df = df.groupby("category_label", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("revenue", ascending=False)
    top_df = category_df.head(7).copy()
    others_revenue = category_df.iloc[7:]["revenue"].sum()
    if others_revenue > 0:
        top_df = pd.concat([top_df, pd.DataFrame([{"category_label": "Outras", "revenue": others_revenue}])], ignore_index=True)

    top_df["share_pct"] = (top_df["revenue"] / top_df["revenue"].sum()) * 100
    top_df = top_df.sort_values("share_pct", ascending=True)

    fig = px.bar(
        top_df,
        x="share_pct",
        y="category_label",
        orientation="h",
        title="Participação de receita por categoria",
        labels={"share_pct": "Participação (%)", "category_label": "Categoria"},
        text=top_df["share_pct"].map(lambda value: f"{value:.1f}%"),
        color="category_label",
        color_discrete_sequence=[
            COLORS["primary"],
            COLORS["secondary"],
            COLORS["teal"],
            COLORS["highlight"],
            COLORS["success"],
            "#2563EB",
            "#475569",
            "#64748B",
        ],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig = base_layout(fig, show_legend=False)
    fig.update_layout(
        margin=dict(l=24, r=52, t=72, b=32),
        height=440,
    )
    fig.update_xaxes(range=[0, max(55, float(top_df["share_pct"].max()) + 5)])
    return fig


def chart_category_value_vs_satisfaction(df: pd.DataFrame) -> go.Figure:
    category_df = (
        df.groupby("category_label", as_index=False)
        .agg(avg_price=("price", "mean"), orders=("order_id", "nunique"), avg_review=("review_score_mean", "mean"), revenue=("total_item_value", "sum"))
        .query("orders >= 40")
    )
    fig = px.scatter(
        category_df,
        x="avg_price",
        y="avg_review",
        size="orders",
        color="revenue",
        hover_name="category_label",
        title="Onde alto volume encontra baixa satisfação",
        labels={"avg_price": "Preço médio", "avg_review": "Nota média", "revenue": "Receita"},
        color_continuous_scale=[[0, "#DBEAFE"], [0.5, "#93C5FD"], [1, COLORS["primary"]]],
    )
    return base_layout(fig)


def chart_state_revenue(df: pd.DataFrame) -> go.Figure:
    state_df = build_state_table(df).head(12).sort_values("receita")
    fig = px.bar(state_df, x="receita", y="uf", orientation="h", title="Quais estados geram mais receita", labels={"uf": "UF", "receita": "Receita"}, color_discrete_sequence=[COLORS["primary"]])
    return base_layout(fig)


def chart_state_delivery_time(df: pd.DataFrame) -> go.Figure:
    state_df = build_state_table(df).query("pedidos >= 80").sort_values("prazo_medio", ascending=False).head(12).sort_values("prazo_medio")
    fig = px.bar(
        state_df,
        x="prazo_medio",
        y="uf",
        orientation="h",
        title="Quais estados têm pior prazo médio de entrega",
        labels={"uf": "UF", "prazo_medio": "Prazo médio (dias)"},
        color_discrete_sequence=[COLORS["highlight"]],
    )
    return base_layout(fig)


def chart_state_delay_rate(df: pd.DataFrame) -> go.Figure:
    state_df = build_state_table(df).query("pedidos >= 80").sort_values("atraso_pct", ascending=False).head(12).sort_values("atraso_pct")
    fig = px.bar(
        state_df,
        x="atraso_pct",
        y="uf",
        orientation="h",
        title="Quais estados concentram maior taxa de atraso",
        labels={"uf": "UF", "atraso_pct": "Taxa de atraso (%)"},
        color_discrete_sequence=[COLORS["danger"]],
    )
    return base_layout(fig)


def chart_delivery_boxplot(df: pd.DataFrame) -> go.Figure:
    delivered = to_order_level(df)
    delivered = delivered[delivered["order_delivered_customer_date"].notna()].copy()
    fig = px.box(
        delivered,
        x="order_status",
        y="delivery_time_days",
        color="order_status",
        title="Qual a distribuição dos prazos de entrega",
        labels={"order_status": "Status do pedido", "delivery_time_days": "Prazo de entrega (dias)"},
    )
    fig.update_layout(showlegend=False)
    return base_layout(fig)


def chart_delay_by_category(df: pd.DataFrame) -> go.Figure:
    delivered = to_order_level(df)
    delivered = delivered[delivered["order_delivered_customer_date"].notna()].copy()
    category_df = (
        delivered.groupby("category_label", as_index=False)
        .agg(delay_rate=("is_delayed", "mean"), orders=("order_id", "nunique"))
        .query("orders >= 50")
        .sort_values("delay_rate", ascending=False)
        .head(12)
        .sort_values("delay_rate")
    )
    category_df["delay_rate"] = category_df["delay_rate"] * 100
    fig = px.bar(category_df, x="delay_rate", y="category_label", orientation="h", title="Quais categorias concentram mais atrasos", labels={"delay_rate": "Taxa de atraso (%)", "category_label": "Categoria"}, color_discrete_sequence=[COLORS["highlight"]])
    return base_layout(fig)


def chart_delivery_vs_review(df: pd.DataFrame) -> go.Figure:
    delivered = to_order_level(df)
    delivered = delivered[delivered["order_delivered_customer_date"].notna()].copy()
    category_df = (
        delivered.groupby("category_label", as_index=False)
        .agg(avg_delivery=("delivery_time_days", "mean"), avg_review=("review_score_mean", "mean"), orders=("order_id", "nunique"))
        .query("orders >= 40")
    )
    fig = px.scatter(
        category_df,
        x="avg_delivery",
        y="avg_review",
        size="orders",
        color="orders",
        hover_name="category_label",
        title="Existe relação entre atraso e avaliação",
        labels={"avg_delivery": "Prazo médio de entrega", "avg_review": "Nota média", "orders": "Pedidos"},
        color_continuous_scale=[[0, "#D1FAE5"], [0.5, "#6EE7B7"], [1, COLORS["teal"]]],
    )
    return base_layout(fig)
