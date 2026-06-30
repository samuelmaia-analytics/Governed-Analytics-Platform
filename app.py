from __future__ import annotations

from pathlib import Path

import streamlit as st

from pages._shared import (
    DATA_CLASSIFICATION_PATH,
    PIPELINE_LOG_PATH,
    PRIVACY_RISK_PATH,
    PROJECT_ROOT,
    QUALITY_CHECKS_PATH,
    SCHEMA_CONTRACT_RESULTS_PATH,
    count_statuses,
    file_status,
    format_datetime,
    read_csv_safe,
    read_json_safe,
    relative_path,
    render_file_warning,
)

PUBLISHED_MONITORING_PATH = (
    PROJECT_ROOT / "data/published/monitoring/published_layer_monitoring.csv"
)
GOVERNANCE_SCORECARDS_PATH = (
    PROJECT_ROOT / "data/published/monitoring/governance_scorecards.csv"
)
PUBLICATION_DECISION_PATH = (
    PROJECT_ROOT / "data/published/monitoring/publication_decision.json"
)
SCHEMA_CONTRACT_REPORT_PATH = PROJECT_ROOT / "docs/reports/schema_contract_report.md"
WORKFLOWS_DIR = PROJECT_ROOT / "workflows/n8n"

st.set_page_config(
    page_title="Governed Analytics Platform",
    page_icon=":material/policy:",
    layout="wide",
)


def _read_first_csv(paths: list[Path]):
    for path in paths:
        df = read_csv_safe(path)
        if not df.empty:
            return df, path
    return read_csv_safe(Path("__missing__.csv")), None


def _read_first_json(paths: list[Path]):
    for path in paths:
        payload = read_json_safe(path)
        if payload:
            return payload, path
    return {}, None


def _read_schema_contract_results():
    df = read_csv_safe(SCHEMA_CONTRACT_RESULTS_PATH)
    if not df.empty:
        return df, SCHEMA_CONTRACT_RESULTS_PATH

    if not SCHEMA_CONTRACT_REPORT_PATH.exists():
        return df, None

    rows = []
    for line in SCHEMA_CONTRACT_REPORT_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        cells = [
            cell.strip().strip("`").strip("*")
            for cell in stripped.strip("|").split("|")
        ]
        if len(cells) < 4:
            continue
        dataset, check_name, status = cells[:3]
        rows.append(
            {
                "dataset_name": dataset,
                "check_name": check_name,
                "status": status,
                "details": " | ".join(cells[3:]),
            }
        )
    import pandas as pd

    return pd.DataFrame(rows), SCHEMA_CONTRACT_REPORT_PATH if rows else None


def _latest_pipeline_status() -> tuple[str, str]:
    logs, _ = _read_first_csv([PIPELINE_LOG_PATH])
    if logs.empty:
        decision, _ = _read_first_json([PUBLICATION_DECISION_PATH])
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
    checks, _ = _read_first_csv([QUALITY_CHECKS_PATH, PUBLISHED_MONITORING_PATH])
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
    classification_df, _ = _read_first_csv([DATA_CLASSIFICATION_PATH])
    risk_payload, _ = _read_first_json([PRIVACY_RISK_PATH, PUBLICATION_DECISION_PATH])
    contracts_df, _ = _read_schema_contract_results()
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
        decision, decision_source = _read_first_json([PUBLICATION_DECISION_PATH])
        if decision and pipeline_status == str(decision.get("status", "")).upper():
            st.info(
                "Runtime pipeline logs were not found. The latest available "
                "publication decision is shown instead."
            )
            exec_col1, exec_col2, exec_col3 = st.columns(3)
            exec_col1.metric("Decision status", pipeline_status)
            exec_col2.metric("Dataset", decision.get("dataset", "N/A"))
            exec_col3.metric("Decision timestamp", pipeline_timestamp)

            decision_reason = str(decision.get("decision_reason", "")).strip()
            if decision_reason:
                st.warning(decision_reason)
            if decision_source:
                st.caption(
                    f"Fallback source: `{relative_path(decision_source)}`. "
                    "This is versioned governance evidence, not a fresh n8n execution log."
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
