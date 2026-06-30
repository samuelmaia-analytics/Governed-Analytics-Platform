from __future__ import annotations

import pandas as pd
import streamlit as st

from streamlit_shared import (
    PIPELINE_LOG_PATH,
    PROJECT_ROOT,
    count_statuses,
    format_datetime,
    read_csv_safe,
    read_json_safe,
    relative_path,
    render_file_warning,
)

PUBLICATION_DECISION_PATH = (
    PROJECT_ROOT / "data/published/monitoring/publication_decision.json"
)

st.title("Pipeline Logs")
st.caption(
    "Execution history registered by local scripts or n8n command orchestration."
)

logs_df = read_csv_safe(PIPELINE_LOG_PATH)

if logs_df.empty:
    decision = read_json_safe(PUBLICATION_DECISION_PATH)
    if not decision:
        render_file_warning(
            PIPELINE_LOG_PATH,
            "Run `python scripts/register_pipeline_log.py` or the n8n workflow to create history.",
        )
        st.stop()

    st.info(
        "Runtime execution logs were not found. Showing the latest versioned "
        f"publication decision from `{relative_path(PUBLICATION_DECISION_PATH)}`."
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest status", str(decision.get("status", "review")).upper())
    col2.metric("Dataset", decision.get("dataset", "N/A"))
    col3.metric("Quality score", decision.get("quality_score", "N/A"))
    col4.metric("Privacy risk score", decision.get("privacy_risk_score", "N/A"))

    if decision.get("timestamp_utc"):
        st.caption(f"Timestamp: {format_datetime(decision.get('timestamp_utc'))}")
    if decision.get("decision_reason"):
        st.warning(str(decision["decision_reason"]))

    st.subheader("Publication decision payload")
    st.json(decision)
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
