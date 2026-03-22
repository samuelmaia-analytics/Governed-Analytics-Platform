from __future__ import annotations

import pandas as pd

from streamlit_app.data import FilterState, filter_dataframe, get_previous_period_df


def build_filter_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "category_label": ["Cat A", "Cat B", "Cat A"],
            "customer_state": ["SP", "RJ", "SP"],
            "seller_state": ["MG", "RJ", "SP"],
            "price": [100.0, 200.0, 50.0],
            "freight_value": [10.0, 20.0, 5.0],
            "order_status": ["delivered", "shipped", "delivered"],
            "payment_type_mode": ["credit_card", "boleto", "credit_card"],
            "order_purchase_timestamp": pd.to_datetime(["2018-01-10", "2018-01-11", "2018-01-05"]),
        }
    )


def test_filter_dataframe_respects_selected_customer_state_and_category() -> None:
    df = build_filter_frame()
    filters = FilterState(
        start_date=pd.Timestamp("2018-01-09"),
        end_date=pd.Timestamp("2018-01-11"),
        categories=["Cat A"],
        states=["SP"],
        price_range=(0.0, 150.0),
        freight_range=(0.0, 15.0),
        order_status=["delivered"],
        payment_types=["credit_card"],
        geography_mode="Cliente",
    )

    result = filter_dataframe(df, filters)

    assert len(result) == 1
    assert result.iloc[0]["order_id"] == "o1"
    assert result.iloc[0]["selected_state"] == "SP"


def test_get_previous_period_df_builds_previous_window_with_same_filters() -> None:
    df = build_filter_frame()
    filters = FilterState(
        start_date=pd.Timestamp("2018-01-07"),
        end_date=pd.Timestamp("2018-01-08"),
        categories=["Cat A"],
        states=["SP"],
        price_range=(0.0, 150.0),
        freight_range=(0.0, 15.0),
        order_status=["delivered"],
        payment_types=["credit_card"],
        geography_mode="Cliente",
    )

    result = get_previous_period_df(df, filters)

    assert len(result) == 1
    assert result.iloc[0]["order_id"] == "o3"
