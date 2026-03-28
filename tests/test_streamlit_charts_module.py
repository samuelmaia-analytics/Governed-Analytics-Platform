from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from streamlit_app import charts


def build_chart_frame() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    categories = ["Bed Bath Table", "Health Beauty", "Sports Leisure"]
    states = ["SP", "RJ", "MG"]
    for month in [1, 2, 3]:
        for state_index, state in enumerate(states):
            category = categories[state_index]
            for order_index in range(45):
                delivered = order_index % 5 != 0
                rows.append(
                    {
                        "order_id": f"{month}-{state}-{order_index}",
                        "customer_unique_id": f"c-{month}-{state}-{order_index}",
                        "selected_state": state,
                        "category_label": category,
                        "payment_type_mode": "credit_card",
                        "order_status": "delivered" if delivered else "processing",
                        "order_purchase_timestamp": pd.Timestamp(2018, month, 10),
                        "order_delivered_customer_date": pd.Timestamp(2018, month, 15)
                        if delivered
                        else pd.NaT,
                        "delivery_time_days": 4.0 + state_index,
                        "is_delayed": state == "RJ",
                        "review_score_mean": 3.5 + state_index * 0.3,
                        "total_item_value": 100.0 + state_index + order_index,
                        "freight_value": 10.0 + state_index,
                        "price": 90.0 + order_index,
                        "month_start": pd.Timestamp(2018, month, 1),
                        "quarter_label": "2018 Q1",
                    }
                )
    return pd.DataFrame(rows)


def test_base_layout_applies_standard_visual_defaults() -> None:
    fig = charts.base_layout(go.Figure())

    assert fig.layout.paper_bgcolor == charts.COLORS["surface"]
    assert fig.layout.plot_bgcolor == charts.COLORS["surface"]
    assert fig.layout.height == 375


def test_chart_functions_return_plotly_figures() -> None:
    df = build_chart_frame()

    chart_builders = [
        charts.chart_revenue_line,
        charts.chart_orders_area,
        charts.chart_seasonality_heatmap,
        charts.chart_delay_by_period,
        charts.chart_top_categories_revenue,
        charts.chart_top_categories_orders,
        charts.chart_category_share_donut,
        charts.chart_category_value_vs_satisfaction,
        charts.chart_state_revenue,
        charts.chart_state_delivery_time,
        charts.chart_state_delay_rate,
        charts.chart_delivery_boxplot,
        charts.chart_delay_by_category,
        charts.chart_delivery_vs_review,
    ]

    for chart_builder in chart_builders:
        fig = chart_builder(df)
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text


def test_chart_category_share_donut_groups_long_tail_into_outras() -> None:
    df = pd.DataFrame(
        {
            "category_label": [f"Cat {index}" for index in range(9)],
            "total_item_value": [10.0] * 9,
        }
    )

    fig = charts.chart_category_share_donut(df)

    labels = [label for trace in fig.data for label in trace["y"]]
    assert "Outras" in labels
