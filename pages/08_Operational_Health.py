from __future__ import annotations

import pandas as pd
import streamlit as st

from streamlit_shared import (
    PIPELINE_LOG_PATH,
    format_datetime,
    read_csv_safe,
    relative_path,
    render_artifact_diagnostics,
)


def _numeric_sum(df: pd.DataFrame, column: str) -> int:
    if column not in df.columns:
        return 0
    return int(pd.to_numeric(df[column], errors="coerce").fillna(0).sum())


def _numeric_mean(df: pd.DataFrame, column: str) -> str:
    if column not in df.columns:
        return "N/A"
    values = pd.to_numeric(df[column], errors="coerce").dropna()
    if values.empty:
        return "N/A"
    return f"{values.mean():.1f}"


def _latest_execution(df: pd.DataFrame) -> pd.Series:
    if "finished_at" in df.columns:
        sortable = df.copy()
        sortable["_finished_at"] = pd.to_datetime(
            sortable["finished_at"], errors="coerce"
        )
        sortable = sortable.sort_values("_finished_at", na_position="first")
        return sortable.drop(columns=["_finished_at"]).tail(1).iloc[0]
    return df.tail(1).iloc[0]


def _count_status(df: pd.DataFrame, statuses: set[str]) -> int:
    if "status" not in df.columns:
        return 0
    normalized = df["status"].fillna("").astype(str).str.upper()
    return int(normalized.isin(statuses).sum())


st.title("Operational Health")
st.caption(
    "Operational view based on controlled pipeline execution logs. "
    "No synthetic fallback data is generated when logs are missing."
)

logs_df = read_csv_safe(PIPELINE_LOG_PATH)

if logs_df.empty:
    st.info(
        f"No pipeline execution log found at `{relative_path(PIPELINE_LOG_PATH)}`. "
        "Run the pipeline or use the versioned example logs to populate this page."
    )
    render_artifact_diagnostics()
    st.stop()

latest = _latest_execution(logs_df)
latest_status = str(latest.get("status", "unknown")).upper()
latest_dataset = latest.get("dataset_name", latest.get("pipeline_name", "N/A"))
latest_finished_at = latest.get("finished_at", latest.get("timestamp_utc", ""))
latest_duration = latest.get("duration_seconds", "N/A")

st.subheader("Last execution")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Status", latest_status)
col2.metric("Dataset / pipeline", latest_dataset)
col3.metric("Duration (s)", latest_duration)
col4.metric("Finished at", format_datetime(latest_finished_at) or "N/A")

if latest_status in {"FAILED", "ERROR"}:
    st.error(str(latest.get("error_message", "Latest execution failed.")))
elif latest_status in {"WARNING", "WARN"}:
    st.warning(str(latest.get("error_message", "Latest execution requires review.")))
else:
    st.success("Latest execution completed without a blocking status.")

st.subheader("Operational KPIs")
failures = _count_status(logs_df, {"FAILED", "ERROR"})
warnings = _count_status(logs_df, {"WARNING", "WARN"})
rows_processed = _numeric_sum(logs_df, "rows_processed")
records_rejected = _numeric_sum(logs_df, "records_rejected")
quality_avg = _numeric_mean(logs_df, "quality_score")
lgpd_avg = _numeric_mean(logs_df, "lgpd_risk_score")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total failures", failures)
kpi2.metric("Total warnings", warnings)
kpi3.metric("Rows processed", f"{rows_processed:,}")
kpi4.metric("Records rejected", f"{records_rejected:,}")

kpi5, kpi6 = st.columns(2)
kpi5.metric("Average quality score", quality_avg)
kpi6.metric("Average LGPD risk score", lgpd_avg)

st.subheader("Status by execution")
if "status" in logs_df.columns:
    status_counts = (
        logs_df["status"]
        .fillna("unknown")
        .astype(str)
        .str.upper()
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
    )
    st.bar_chart(status_counts.set_index("status"))
else:
    st.info("Column `status` not found in the pipeline log.")

st.subheader("Execution history")
display_df = logs_df.copy()
for column in ["started_at", "finished_at", "timestamp_utc"]:
    if column in display_df.columns:
        display_df[column] = display_df[column].map(format_datetime)
st.dataframe(display_df.sort_index(ascending=False), width="stretch", hide_index=True)

st.caption(
    f"Source: `{relative_path(PIPELINE_LOG_PATH)}`. Values are operational evidence "
    "from local/versioned logs, not a claim of live production monitoring."
)

render_artifact_diagnostics()
