from __future__ import annotations

import pandas as pd

from streamlit_app.data import FilterState
from streamlit_app.formatting import (
    calc_delta,
    format_currency,
    format_currency_compact,
    format_number,
    format_pct,
)


def to_order_level(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("order_purchase_timestamp").drop_duplicates(subset=["order_id"], keep="last").copy()


def safe_mean(series: pd.Series) -> float | None:
    if series.empty:
        return None
    value = series.mean()
    if pd.isna(value):
        return None
    return float(value)


def non_placeholder_mask(series: pd.Series) -> pd.Series:
    normalized = series.fillna("").astype(str).str.strip()
    return ~normalized.isin({"", "NA", "unknown", "Unknown", "nan", "NaN"})


def build_metrics(current_df: pd.DataFrame, previous_df: pd.DataFrame) -> list[dict[str, str]]:
    current_orders = to_order_level(current_df)
    previous_orders = to_order_level(previous_df)
    current_delivered = current_orders[current_orders["order_delivered_customer_date"].notna()].copy()
    previous_delivered = previous_orders[previous_orders["order_delivered_customer_date"].notna()].copy()

    revenue = float(current_df["total_item_value"].sum())
    revenue_prev = float(previous_df["total_item_value"].sum())
    total_orders = float(current_orders["order_id"].nunique())
    total_orders_prev = float(previous_orders["order_id"].nunique())
    avg_ticket = revenue / total_orders if total_orders else 0.0
    avg_ticket_prev = revenue_prev / total_orders_prev if total_orders_prev else 0.0
    customers = float(current_orders["customer_unique_id"].nunique())
    customers_prev = float(previous_orders["customer_unique_id"].nunique())
    avg_delivery = safe_mean(current_delivered["delivery_time_days"])
    avg_delivery_prev = safe_mean(previous_delivered["delivery_time_days"])
    delay_rate_base = safe_mean(current_delivered["is_delayed"])
    delay_rate_prev_base = safe_mean(previous_delivered["is_delayed"])
    delay_rate = delay_rate_base * 100 if delay_rate_base is not None else None
    delay_rate_prev = delay_rate_prev_base * 100 if delay_rate_prev_base is not None else None
    avg_review = safe_mean(current_orders["review_score_mean"])
    avg_review_prev = safe_mean(previous_orders["review_score_mean"])
    avg_freight = safe_mean(current_df["freight_value"])
    avg_freight_prev = safe_mean(previous_df["freight_value"])

    return [
        {"label": "Receita total", "value": format_currency_compact(revenue), "delta": calc_delta(revenue, revenue_prev), "delta_color": "normal", "help": "Soma de item e frete no recorte filtrado."},
        {"label": "Total de pedidos", "value": format_number(total_orders), "delta": calc_delta(total_orders, total_orders_prev), "delta_color": "normal", "help": "Quantidade única de pedidos no período."},
        {"label": "Ticket médio", "value": format_currency(avg_ticket), "delta": calc_delta(avg_ticket, avg_ticket_prev), "delta_color": "normal", "help": "Receita total dividida pelo número de pedidos."},
        {"label": "Total de clientes", "value": format_number(customers), "delta": calc_delta(customers, customers_prev), "delta_color": "normal", "help": "Clientes únicos no recorte filtrado."},
        {"label": "Prazo médio", "value": f"{avg_delivery:.1f} dias" if avg_delivery is not None else "N/A", "delta": calc_delta(avg_delivery, avg_delivery_prev), "delta_color": "inverse", "help": "Tempo médio entre compra e entrega para pedidos entregues."},
        {"label": "Taxa de atraso", "value": format_pct(delay_rate) if delay_rate is not None else "N/A", "delta": calc_delta(delay_rate, delay_rate_prev), "delta_color": "inverse", "help": "Percentual de pedidos entregues após a data estimada."},
        {"label": "Nota média", "value": f"{avg_review:.2f}" if avg_review is not None else "N/A", "delta": calc_delta(avg_review, avg_review_prev), "delta_color": "normal", "help": "Média de review em nível de pedido."},
        {"label": "Frete médio por item", "value": format_currency(avg_freight) if avg_freight is not None else "N/A", "delta": calc_delta(avg_freight, avg_freight_prev), "delta_color": "inverse", "help": "Valor médio de frete por item vendido."},
    ]


def build_smart_summary(df: pd.DataFrame) -> dict[str, object]:
    order_level = to_order_level(df)
    delivered = order_level[order_level["order_delivered_customer_date"].notna()].copy()
    category_source = df.loc[non_placeholder_mask(df["category_label"])].copy()
    category_perf = (
        category_source.groupby("category_label", as_index=False)
        .agg(revenue=("total_item_value", "sum"), orders=("order_id", "nunique"), avg_review=("review_score_mean", "mean"))
        .sort_values("revenue", ascending=False)
    )
    top_category = category_perf.iloc[0] if not category_perf.empty else None

    monthly = df.groupby("month_start", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("month_start")
    trend_text = "Série temporal insuficiente para leitura de tendência."
    if len(monthly) >= 2:
        latest = float(monthly.iloc[-1]["revenue"])
        previous = float(monthly.iloc[-2]["revenue"])
        delta = ((latest / previous) - 1) * 100 if previous else 0
        if delta > 5:
            trend_text = f"A receita no fim do recorte acelera {delta:.1f}% frente ao mês anterior."
        elif delta < -5:
            trend_text = f"A receita no fim do recorte recua {abs(delta):.1f}% frente ao mês anterior."
        else:
            trend_text = f"A receita no fim do recorte permanece estável, com variação de {delta:.1f}%."

    state_source = df.loc[non_placeholder_mask(df["selected_state"])].copy()
    state_perf = (
        state_source.groupby("selected_state", as_index=False)
        .agg(revenue=("total_item_value", "sum"), avg_review=("review_score_mean", "mean"))
        .sort_values("revenue", ascending=False)
    )
    top_state = state_perf.iloc[0] if not state_perf.empty else None

    logistics = (
        delivered.loc[non_placeholder_mask(delivered["category_label"])].groupby("category_label", as_index=False)
        .agg(delayed_pct=("is_delayed", "mean"), avg_delivery_time=("delivery_time_days", "mean"), orders=("order_id", "nunique"))
        .query("orders >= 30")
        .sort_values(["delayed_pct", "avg_delivery_time"], ascending=[False, False])
    )
    top_logistics = logistics.iloc[0] if not logistics.empty else None

    recommendations: list[str] = []
    if top_category is not None:
        recommendations.append(
            f"Proteger {top_category['category_label']} com revisão de estoque, preço e disponibilidade, porque ela lidera a geração de receita."
        )
    if top_state is not None:
        recommendations.append(
            f"Priorizar a operação em {top_state['selected_state']}, principal praça comercial do recorte, com revisão de frete e SLA."
        )
    if top_logistics is not None and float(top_logistics["delayed_pct"]) * 100 > 12:
        recommendations.append(
            f"Abrir diagnóstico logístico em {top_logistics['category_label']}, que concentra o maior alerta de atraso."
        )
    avg_review = safe_mean(order_level["review_score_mean"]) or 0
    if avg_review and avg_review < 4.0:
        recommendations.append(
            "Cruzar reviews, atraso e status de pedido para identificar a principal causa de deterioração da satisfação."
        )
    if not recommendations:
        recommendations.append(
            "O recorte atual está equilibrado; a melhor oportunidade é aprofundar segmentações por estado, categoria e pagamento."
        )

    return {
        "summary": " ".join(
            [
                f"A categoria líder é {top_category['category_label']}, com {format_currency(float(top_category['revenue']))}." if top_category is not None else "Sem categoria líder disponível.",
                trend_text,
                f"A praça mais forte é {top_state['selected_state']}, concentrando {format_currency(float(top_state['revenue']))}." if top_state is not None else "Sem destaque geográfico disponível.",
                f"O principal gargalo logístico está em {top_logistics['category_label']}, com {format_pct(float(top_logistics['delayed_pct']) * 100)} de atraso." if top_logistics is not None else "Sem alerta logístico relevante no recorte.",
            ]
        ),
        "chips": [
            {"label": "Top categoria", "value": f"{top_category['category_label']} • {format_currency(float(top_category['revenue']))}" if top_category is not None else "N/A"},
            {"label": "Tendência temporal", "value": trend_text},
            {"label": "Região mais forte", "value": f"{top_state['selected_state']} • {format_currency(float(top_state['revenue']))}" if top_state is not None else "N/A"},
            {"label": "Alerta logístico", "value": f"{top_logistics['category_label']} • {format_pct(float(top_logistics['delayed_pct']) * 100)}" if top_logistics is not None else "N/A"},
        ],
        "recommendations": recommendations[:4],
    }


def build_filter_context_summary(df: pd.DataFrame, filters: FilterState) -> list[tuple[str, str]]:
    orders = to_order_level(df)
    return [
        ("Período", f"{filters.start_date:%d/%m/%Y} a {filters.end_date:%d/%m/%Y}"),
        ("Categorias", format_number(len(filters.categories))),
        ("Estados", format_number(len(filters.states))),
        ("Pedidos no recorte", format_number(orders["order_id"].nunique())),
    ]


def build_state_table(df: pd.DataFrame) -> pd.DataFrame:
    order_level = to_order_level(df)
    delivered = order_level[order_level["order_delivered_customer_date"].notna()].copy()
    state_df = (
        df.groupby("selected_state", as_index=False)
        .agg(receita=("total_item_value", "sum"), pedidos=("order_id", "nunique"), clientes=("customer_unique_id", "nunique"), frete_medio=("freight_value", "mean"))
        .merge(
            delivered.groupby("selected_state", as_index=False).agg(prazo_medio=("delivery_time_days", "mean"), atraso_pct=("is_delayed", "mean"), review_medio=("review_score_mean", "mean")),
            on="selected_state",
            how="left",
        )
        .sort_values("receita", ascending=False)
    )
    state_df["atraso_pct"] = state_df["atraso_pct"] * 100
    state_df["ticket_medio"] = state_df["receita"] / state_df["pedidos"].replace(0, pd.NA)
    return state_df.rename(columns={"selected_state": "uf"})


def build_regional_insights(df: pd.DataFrame) -> list[str]:
    state_df = build_state_table(df).query("pedidos >= 80").copy()
    if state_df.empty:
        return ["O recorte filtrado não possui massa suficiente por UF para uma leitura regional robusta."]

    top_revenue = state_df.sort_values("receita", ascending=False).iloc[0]
    worst_delay = state_df.sort_values("atraso_pct", ascending=False).iloc[0]
    highest_freight = state_df.sort_values("frete_medio", ascending=False).iloc[0]
    lowest_review = state_df.sort_values("review_medio", ascending=True).iloc[0]

    return [
        f"{top_revenue['uf']} lidera em receita e deve ser tratada como praça prioritária para captura de valor e eficiência comercial.",
        f"{worst_delay['uf']} apresenta a pior taxa de atraso entre as principais UFs, sinalizando prioridade operacional imediata.",
        f"{highest_freight['uf']} concentra o frete médio mais alto no recorte, o que pode pressionar margem e percepção de valor.",
        f"{lowest_review['uf']} registra a menor satisfação média e merece investigação cruzando SLA, frete e status de pedido.",
    ]


def build_executive_insights(df: pd.DataFrame) -> list[dict[str, str]]:
    order_level = to_order_level(df)
    delivered = order_level[order_level["order_delivered_customer_date"].notna()].copy()

    category_summary = (
        df.loc[non_placeholder_mask(df["category_label"])].groupby("category_label", as_index=False)
        .agg(revenue=("total_item_value", "sum"), orders=("order_id", "nunique"), avg_review=("review_score_mean", "mean"))
        .sort_values("revenue", ascending=False)
    )
    risky_category_df = category_summary.query("orders >= 40").sort_values(["avg_review", "revenue"], ascending=[True, False])
    risky_category = risky_category_df.iloc[0] if not risky_category_df.empty else None

    state_summary = (
        delivered.loc[non_placeholder_mask(delivered["selected_state"])].groupby("selected_state", as_index=False)
        .agg(revenue=("total_item_value", "sum"), avg_delivery=("delivery_time_days", "mean"), avg_review=("review_score_mean", "mean"))
        .sort_values("revenue", ascending=False)
    )
    slow_state_df = state_summary.query("revenue > 0").sort_values(["avg_delivery", "revenue"], ascending=[False, False])
    slow_state = slow_state_df.iloc[0] if not slow_state_df.empty else None

    pay_summary = (
        df.loc[non_placeholder_mask(df["payment_type_mode"])]
        .groupby("payment_type_mode", as_index=False)
        .agg(revenue=("total_item_value", "sum"))
        .sort_values("revenue", ascending=False)
    )
    top_payment = pay_summary.iloc[0] if not pay_summary.empty else None

    monthly = df.groupby("month_start", as_index=False).agg(revenue=("total_item_value", "sum")).sort_values("month_start")
    growth_text = "A série atual não tem massa suficiente para comparação temporal robusta."
    if len(monthly) >= 2:
        latest = float(monthly.iloc[-1]["revenue"])
        previous = float(monthly.iloc[-2]["revenue"])
        delta = ((latest / previous) - 1) * 100 if previous else 0
        if delta >= 5:
            growth_text = f"O recorte encerra com aceleração de {delta:.1f}% na receita frente ao mês anterior."
        elif delta <= -5:
            growth_text = f"O recorte encerra com retração de {abs(delta):.1f}% na receita frente ao mês anterior."
        else:
            growth_text = f"O recorte encerra com estabilidade relativa, variando {delta:.1f}% na receita."

    return [
        {"title": "Sinal comercial", "text": growth_text},
        {"title": "Risco por categoria", "text": f"{risky_category['category_label']} combina relevância comercial com satisfação abaixo da média e deve ser tratada como prioridade de experiência." if risky_category is not None else "Não houve categoria com volume suficiente para um alerta de risco consistente no recorte."},
        {"title": "Gargalo regional", "text": f"{slow_state['selected_state']} aparece como praça de alto peso com prazo médio elevado, sugerindo ganho operacional direto com revisão de SLA regional." if slow_state is not None else "Não houve concentração regional relevante para um alerta operacional claro."},
        {"title": "Dependência de pagamento", "text": f"{top_payment['payment_type_mode']} lidera a captura de receita, reforçando a importância de manter checkout, aprovação e conciliação sem fricção." if top_payment is not None else "Não foi possível identificar concentração relevante por meio de pagamento."},
    ]
