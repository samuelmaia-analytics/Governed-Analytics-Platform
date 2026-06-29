from __future__ import annotations

import pandas as pd
import streamlit as st

from pages._shared import (
    PIPELINE_LOG_PATH,
    count_statuses,
    format_datetime,
    read_csv_safe,
    render_file_warning,
)

st.set_page_config(page_title="Pipeline Logs | Governed Analytics", layout="wide")

st.title("Pipeline Logs")
st.caption(
    "Execution history registered by local scripts or n8n command orchestration."
)

logs_df = read_csv_safe(PIPELINE_LOG_PATH)

if logs_df.empty:
    render_file_warning(
        PIPELINE_LOG_PATH,
        "Run `python scripts/register_pipeline_log.py` or the n8n workflow to create history.",
    )
    st.stop()

latest = logs_df.tail(1).iloc[0]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest status", str(latest.get("status", "unknown")).upper())
col2.metric("Latest source", latest.get("source", "N/A"))
col3.metric("Duration", latest.get("duration_seconds", "N/A"))
col4.metric("Timestamp", format_datetime(latest.get("timestamp_utc", "")) or "N/A")

message = str(latest.get("message", ""))
if "error" in logs_df.columns and str(latest.get("error", "")).strip():
    st.error(str(latest.get("error")))
elif str(latest.get("status", "")).lower() in {"failed", "error"}:
    st.error(message or "Latest execution failed. No detailed error column was found.")
elif str(latest.get("status", "")).lower() == "success":
    st.success(message or "Latest execution completed successfully.")
else:
    st.warning(message or "Latest execution status requires review.")

missing_operational_cols = [
    col
    for col in ["duration_seconds", "errors", "warnings"]
    if col not in logs_df.columns
]
if missing_operational_cols:
    st.info(
        "The current log file does not include these optional operational fields: "
        + ", ".join(missing_operational_cols)
        + ". The dashboard shows available evidence only."
    )

st.subheader("Status history")
status_counts = count_statuses(logs_df)
if status_counts:
    status_df = pd.DataFrame(
        [{"status": status, "count": count} for status, count in status_counts.items()]
    )
    st.bar_chart(status_df.set_index("status"))

st.subheader("Execution log table")
st.dataframe(logs_df.sort_index(ascending=False), width="stretch", hide_index=True)
