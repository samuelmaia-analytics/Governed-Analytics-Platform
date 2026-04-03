from __future__ import annotations

import pandas as pd

from streamlit_app.analytics import (
    build_executive_insights,
    build_filter_context_summary,
    build_metrics,
    build_regional_insights,
    build_smart_summary,
    build_state_table,
    safe_mean,
    to_order_level,
)
from streamlit_app.data import FilterState


def build_analytics_frame() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    monthly_revenue = [100.0, 120.0, 150.0]
    states = ["SP", "RJ", "MG"]
    categories = ["Bed Bath Table", "Health Beauty", "Sports Leisure"]
    payments = ["credit_card", "boleto", "voucher"]
    for month_index, revenue in enumerate(monthly_revenue, start=1):
        for state_index, state in enumerate(states):
            for order_sequence in range(40):
                order_id = f"o-{month_index}-{state}-{order_sequence}"
                category = categories[state_index]
                review = 3.2 if category == "Bed Bath Table" else 4.6
                delivery = 8.0 if state == "RJ" else 4.0 + state_index
                delayed = state == "RJ"
                rows.append(
                    {
                        "order_id": order_id,
                        "customer_unique_id": f"c-{order_id}",
                        "order_purchase_timestamp": pd.Timestamp(2018, month_index, 10),
                        "order_delivered_customer_date": pd.Timestamp(2018, month_index, 15),
                        "delivery_time_days": delivery,
                        "is_delayed": delayed,
                        "review_score_mean": review,
                        "total_item_value": revenue + order_sequence,
                        "freight_value": 10.0 + state_index,
                        "price": revenue,
                        "category_label": category,
                        "selected_state": state,
                        "payment_type_mode": payments[state_index],
                        "month_start": pd.Timestamp(2018, month_index, 1),
                    }
                )
    return pd.DataFrame(rows)


def test_to_order_level_keeps_last_row_per_order() -> None:
    df = pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "order_purchase_timestamp": pd.to_datetime(["2018-01-01", "2018-01-02", "2018-01-01"]),
            "value": [1, 2, 3],
        }
    )

    result = to_order_level(df)

    assert len(result) == 2
    assert result.loc[result["order_id"] == "o1", "value"].iloc[0] == 2


def test_build_metrics_returns_expected_kpis() -> None:
    current_df = build_analytics_frame()
    previous_df = current_df[current_df["month_start"] == pd.Timestamp(2018, 1, 1)].copy()

    metrics = build_metrics(current_df, previous_df)

    assert len(metrics) == 8
    assert metrics[0]["label"] == "Receita total"
    assert metrics[4]["value"].endswith("dias")
    assert metrics[5]["value"].endswith("%")
    assert metrics[4]["delta_color"] == "inverse"
    assert metrics[5]["delta_color"] == "inverse"
    assert metrics[7]["label"] == "Frete médio por item"


def test_safe_mean_and_build_metrics_handle_nan_bases_without_rendering_nan() -> None:
    current_df = pd.DataFrame(
        {
            "order_id": ["o1"],
            "customer_unique_id": ["c1"],
            "order_purchase_timestamp": pd.to_datetime(["2018-01-01"]),
            "order_delivered_customer_date": [pd.NaT],
            "delivery_time_days": [pd.NA],
            "is_delayed": [pd.NA],
            "review_score_mean": [pd.NA],
            "total_item_value": [10.0],
            "freight_value": [pd.NA],
        }
    )
    previous_df = current_df.copy()

    metrics = build_metrics(current_df, previous_df)

    assert safe_mean(current_df["review_score_mean"]) is None
    assert metrics[4]["value"] == "N/A"
    assert metrics[5]["value"] == "N/A"
    assert metrics[6]["value"] == "N/A"
    assert metrics[7]["value"] == "N/A"
    assert all("nan" not in metric["delta"].lower() for metric in metrics)


def test_build_smart_summary_returns_summary_chips_and_recommendations() -> None:
    summary = build_smart_summary(build_analytics_frame())

    assert "A categoria líder é" in summary["summary"]
    assert len(summary["chips"]) == 4
    assert len(summary["recommendations"]) >= 1


def test_build_filter_context_summary_formats_active_scope() -> None:
    df = build_analytics_frame()
    filters = FilterState(
        start_date=pd.Timestamp("2018-01-01"),
        end_date=pd.Timestamp("2018-03-31"),
        categories=["Bed Bath Table", "Health Beauty"],
        states=["SP", "RJ"],
        price_range=(0.0, 1000.0),
        freight_range=(0.0, 100.0),
        order_status=["delivered"],
        payment_types=["credit_card"],
        geography_mode="Cliente",
    )

    context = build_filter_context_summary(df, filters)

    assert context[0] == ("Período", "01/01/2018 a 31/03/2018")
    assert context[1][1] == "2"
    assert context[2][1] == "2"


def test_build_state_table_aggregates_regional_metrics() -> None:
    state_df = build_state_table(build_analytics_frame())

    assert {"uf", "receita", "pedidos", "ticket_medio", "atraso_pct"}.issubset(state_df.columns)
    assert state_df["uf"].iloc[0] in {"SP", "RJ", "MG"}


def test_build_regional_insights_returns_prioritized_messages() -> None:
    insights = build_regional_insights(build_analytics_frame())

    assert len(insights) == 4
    assert any("prioridade operacional" in text for text in insights)


def test_build_executive_insights_returns_four_cards() -> None:
    cards = build_executive_insights(build_analytics_frame())

    assert [card["title"] for card in cards] == [
        "Sinal comercial",
        "Risco por categoria",
        "Gargalo regional",
        "Dependência de pagamento",
    ]


def test_summaries_and_insights_ignore_placeholder_dimensions() -> None:
    df = build_analytics_frame().copy()
    df["category_label"] = "unknown"
    df["selected_state"] = "NA"
    df["payment_type_mode"] = "unknown"

    summary = build_smart_summary(df)
    cards = build_executive_insights(df)

    assert "Sem categoria líder disponível." in summary["summary"]
    assert "Sem destaque geográfico disponível." in summary["summary"]
    assert cards[1]["text"].startswith("Não houve categoria")
    assert cards[2]["text"].startswith("Não houve concentração regional")
    assert cards[3]["text"].startswith("Não foi possível identificar")
