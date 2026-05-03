from __future__ import annotations

import streamlit as st


def render_metric_cards(metrics: list[dict[str, str]], max_columns: int = 4) -> None:
    if not metrics:
        return
    safe_max_columns = max(1, max_columns)
    for start in range(0, len(metrics), safe_max_columns):
        chunk = metrics[start : start + safe_max_columns]
        columns = st.columns(len(chunk))
        for index, metric in enumerate(chunk):
            with columns[index]:
                st.metric(
                    label=metric["label"],
                    value=metric["value"],
                    delta=metric.get("delta"),
                )
