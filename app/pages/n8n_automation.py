from __future__ import annotations

import streamlit as st

from streamlit_shared import (
    DOCS_DIR,
    PIPELINE_LOG_PATH,
    PUBLICATION_DECISION_PATH,
    WORKFLOWS_DIR,
    file_status,
    read_json_safe,
    relative_path,
    render_artifact_diagnostics,
    render_file_warning,
)


def _workflow_rows(workflow_files):
    rows = []
    for path in workflow_files:
        payload = read_json_safe(path)
        nodes = payload.get("nodes", []) if isinstance(payload, dict) else []
        rows.append(
            {
                "workflow_file": relative_path(path),
                "workflow_name": payload.get("name", path.stem)
                if isinstance(payload, dict)
                else path.stem,
                "status": "importable JSON" if payload else "read error",
                "node_count": len(nodes),
            }
        )
    return rows


def render_n8n_automation() -> None:
    st.title("n8n Automation")
    st.caption("Workflow visibility without executing n8n from Streamlit.")

    st.markdown(
        """
        n8n is represented in this repository as an orchestration layer for the
        governed analytics pipeline. The workflow templates coordinate Python
        scripts, execution metadata, error routing, and alert placeholders.

        The Streamlit app does not execute n8n, does not expose credentials, and
        does not create webhooks. It only displays versioned workflow templates,
        documentation, and available execution/publication artifacts.
        """
    )

    st.subheader("Automation role")
    workflow_steps = [
        "Schedule or manual trigger in n8n",
        "Set execution metadata",
        "Check input dataset availability",
        "Run data quality checks",
        "Run LGPD classification",
        "Run privacy risk scoring",
        "Generate governance documentation",
        "Register execution log",
        "Route success or error notifications through placeholder alert nodes",
    ]
    for index, step in enumerate(workflow_steps, start=1):
        st.write(f"{index}. {step}")

    st.subheader("Artifact status")
    status_rows = [
        file_status("n8n workflows directory", WORKFLOWS_DIR),
        file_status("Pipeline execution logs", PIPELINE_LOG_PATH),
        file_status("Publication decision", PUBLICATION_DECISION_PATH),
        file_status("n8n automation documentation", DOCS_DIR / "n8n_automation.md"),
    ]
    st.dataframe(status_rows, width="stretch", hide_index=True)

    st.subheader("Available workflow JSON files")
    if not WORKFLOWS_DIR.exists():
        render_file_warning(
            WORKFLOWS_DIR,
            "Create or import workflow templates under `workflows/n8n/`.",
        )
        render_artifact_diagnostics()
        return

    workflow_files = sorted(WORKFLOWS_DIR.glob("*.json"))
    if not workflow_files:
        st.warning("Artifact not found: no workflow JSON files under `workflows/n8n/`.")
        render_artifact_diagnostics()
        return

    st.dataframe(_workflow_rows(workflow_files), width="stretch", hide_index=True)

    selected = st.selectbox(
        "Inspect workflow", [relative_path(path) for path in workflow_files]
    )
    selected_path = next(
        path for path in workflow_files if relative_path(path) == selected
    )
    payload = read_json_safe(selected_path)

    if payload:
        st.subheader(str(payload.get("name", selected_path.stem)))
        node_rows = [
            {
                "node": node.get("name", ""),
                "type": node.get("type", ""),
                "notes": node.get("notes", ""),
            }
            for node in payload.get("nodes", [])
        ]
        st.dataframe(node_rows, width="stretch", hide_index=True)

        st.caption(
            "These nodes are versioned workflow definitions. Credentials and "
            "environment-specific activation must be configured in n8n, not in "
            "Streamlit."
        )

        with st.expander("Raw workflow JSON"):
            st.json(payload)
    else:
        st.warning(
            f"Artifact not readable: `{relative_path(selected_path)}` could not be "
            "parsed as JSON."
        )

    render_artifact_diagnostics()
