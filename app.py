from __future__ import annotations

from pathlib import Path

import streamlit as st

from pages._shared import (
    DATA_CLASSIFICATION_PATH,
    GOVERNANCE_SCORECARDS_PATH,
    PIPELINE_LOG_PATH,
    PRIVACY_RISK_PATH,
    PUBLICATION_DECISION_PATH,
    PUBLISHED_MONITORING_PATH,
    QUALITY_CHECKS_PATH,
    WORKFLOWS_DIR,
    count_statuses,
    file_status,
    format_datetime,
    read_first_csv,
    read_first_json,
    read_schema_contract_results,
    render_file_warning,
)

st.set_page_config(
    page_title="Governed Analytics Platform",
    page_icon=":material/policy:",
    layout="wide",
)


def _latest_pipeline_status() -> tuple[str, str]:
    logs, _ = read_first_csv([PIPELINE_LOG_PATH])
    if logs.empty:
        decision, _ = read_first_json([PUBLICATION_DECISION_PATH])
        if decision:
            return (
                str(decision.get("status", "review")).upper(),
                format_datetime(decision.get("timestamp_utc", ""))
                or "Publication decision timestamp not available",
            )
        return "Not available", "No execution log was found."

    latest = logs.tail(1).iloc[0]
    status = str(latest.get("status", "unknown")).upper()
    timestamp = format_datetime(latest.get("timestamp_utc", ""))
    return status, timestamp or "Timestamp not available"


def _quality_summary() -> tuple[int, int, int]:
    checks, _ = read_first_csv([QUALITY_CHECKS_PATH, PUBLISHED_MONITORING_PATH])
    if checks.empty or "status" not in checks.columns:
        return 0, 0, 0
    counts = count_statuses(checks, "status")
    return counts.get("PASS", 0), counts.get("WARN", 0), counts.get("FAIL", 0)


def main() -> None:
    st.title("Governed Analytics Platform")
    st.caption(
        "Executive and technical view for data governance, privacy risk, contracts, "
        "pipeline observability, and n8n orchestration evidence."
    )

    st.markdown(
        """
        This dashboard presents the governed analytics platform as a portfolio-ready
        operating interface. It reads existing project artifacts and shows their
        status without executing n8n or changing pipeline outputs.
        """
    )

    pipeline_status, pipeline_timestamp = _latest_pipeline_status()
    pass_count, warn_count, fail_count = _quality_summary()
    classification_df, _ = read_first_csv([DATA_CLASSIFICATION_PATH])
    risk_payload, _ = read_first_json([PRIVACY_RISK_PATH, PUBLICATION_DECISION_PATH])
    contracts_df, _ = read_schema_contract_results()
    workflows = sorted(WORKFLOWS_DIR.glob("*.json")) if WORKFLOWS_DIR.exists() else []

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Last pipeline status", pipeline_status)
    col2.metric(
        "Data quality checks",
        f"{pass_count} pass / {warn_count} warn / {fail_count} fail",
    )
    col3.metric(
        "LGPD classified fields",
        len(classification_df) if not classification_df.empty else 0,
    )
    col4.metric("n8n workflows", len(workflows))

    col5, col6, col7 = st.columns(3)
    privacy_score = risk_payload.get("score", risk_payload.get("privacy_risk_score", "N/A"))
    risk_level = risk_payload.get("risk_level", risk_payload.get("status", "N/A"))
    col5.metric("Privacy risk score", privacy_score)
    col6.metric("Risk / publication status", str(risk_level).upper())
    contract_counts = (
        count_statuses(contracts_df, "status") if not contracts_df.empty else {}
    )
    col7.metric(
        "Contract checks", sum(contract_counts.values()) if contract_counts else 0
    )

    st.subheader("Last execution")
    if pipeline_status == "Not available":
        render_file_warning(
            PIPELINE_LOG_PATH,
            "Run the pipeline or register an execution log to populate this section.",
        )
    else:
        st.success(
            f"Latest recorded execution: {pipeline_status} at {pipeline_timestamp}"
        )

    st.subheader("Architecture")
    st.markdown(
        """
        - Python and SQL remain responsible for ingestion, validation, classification,
          risk scoring, contracts, documentation, and publication logic.
        - n8n is used only as an orchestration layer: scheduling, command execution,
          metadata capture, error workflow routing, and optional alerts.
        - Streamlit reads generated artifacts from `data/`, `logs/`, `docs/`,
          `contracts/`, and `workflows/n8n/` to support executive review.
        """
    )

    st.subheader("Technologies")
    st.write(
        "Python, pandas, DuckDB, Streamlit, pytest, ruff, LGPD governance rules, "
        "data contracts, Markdown documentation, and n8n workflow templates."
    )

    st.subheader("Artifact availability")
    status_rows = [
        file_status("Quality checks", QUALITY_CHECKS_PATH),
        file_status("Published monitoring fallback", PUBLISHED_MONITORING_PATH),
        file_status("LGPD classification", DATA_CLASSIFICATION_PATH),
        file_status("Privacy risk score", PRIVACY_RISK_PATH),
        file_status("Publication decision fallback", PUBLICATION_DECISION_PATH),
        file_status("Governance scorecards", GOVERNANCE_SCORECARDS_PATH),
        file_status("Pipeline logs", PIPELINE_LOG_PATH),
        file_status("n8n workflows directory", WORKFLOWS_DIR),
        file_status("n8n automation docs", Path("docs/n8n_automation.md")),
    ]
    st.dataframe(status_rows, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
