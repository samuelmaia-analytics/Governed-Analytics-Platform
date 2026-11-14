from __future__ import annotations

import streamlit as st

from app.components.ui import inject_base_styles


def render_metric_cards(metrics: list[dict[str, str | None]], max_columns: int = 4) -> None:
    if not metrics:
        return
    inject_base_styles()
    safe_max_columns = max(1, max_columns)
    for start in range(0, len(metrics), safe_max_columns):
        chunk = metrics[start : start + safe_max_columns]
        columns = st.columns(len(chunk))
        for index, metric in enumerate(chunk):
            with columns[index]:
                with st.container(border=True):
                    st.metric(
                        label=str(metric.get("label", "")),
                        value=str(metric.get("value", "")),
                        delta=metric.get("delta"),
                    )
