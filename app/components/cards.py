from __future__ import annotations

import streamlit as st


def render_metric_cards(metrics: list[dict[str, str]]) -> None:
    columns = st.columns(len(metrics))
    for index, metric in enumerate(metrics):
        with columns[index]:
            st.metric(
                label=metric["label"],
                value=metric["value"],
                delta=metric.get("delta"),
            )
