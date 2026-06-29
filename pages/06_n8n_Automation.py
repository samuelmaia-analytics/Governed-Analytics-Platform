from __future__ import annotations

import streamlit as st

from pages._shared import (
    WORKFLOWS_DIR,
    read_json_safe,
    relative_path,
    render_file_warning,
)

st.set_page_config(page_title="n8n Automation | Governed Analytics", layout="wide")

st.title("n8n Automation")
st.caption("Visibility into workflow templates without executing n8n from Streamlit.")

st.markdown(
    """
    n8n is used as an orchestration layer for the governed analytics pipeline.
    It schedules and coordinates Python scripts, captures execution metadata,
    routes errors to a dedicated workflow, and can be connected to alert channels.

    Streamlit does not execute n8n in this first version. It only displays the
    workflow templates and their expected flow.
    """
)

st.subheader("Pipeline workflow")
workflow_steps = [
    "Schedule Trigger",
    "Set Execution Metadata",
    "Check Input Dataset",
    "Run Data Quality Checks",
    "Run LGPD Classification",
    "Run Privacy Risk Scoring",
    "Generate Governance Docs",
    "Register Execution Log",
    "Send Success Alert",
]
for index, step in enumerate(workflow_steps, start=1):
    st.write(f"{index}. {step}")

st.subheader("Available workflow JSON files")
if not WORKFLOWS_DIR.exists():
    render_file_warning(
        WORKFLOWS_DIR, "Create or import workflow templates under `workflows/n8n/`."
    )
    st.stop()

workflow_files = sorted(WORKFLOWS_DIR.glob("*.json"))
if not workflow_files:
    st.info("No workflow JSON files were found under `workflows/n8n/`.")
    st.stop()

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
st.dataframe(rows, width="stretch", hide_index=True)

selected = st.selectbox(
    "Inspect workflow", [relative_path(path) for path in workflow_files]
)
selected_path = next(path for path in workflow_files if relative_path(path) == selected)
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

    with st.expander("Raw workflow JSON"):
        st.json(payload)
