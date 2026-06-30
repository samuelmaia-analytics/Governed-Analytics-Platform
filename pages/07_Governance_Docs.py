from __future__ import annotations

import streamlit as st

from streamlit_shared import (
    DOCS_DIR,
    markdown_files,
    read_text_safe,
    relative_path,
    render_file_warning,
)

st.title("Governance Docs")
st.caption("Browse generated and versioned Markdown documentation.")

if not DOCS_DIR.exists():
    render_file_warning(
        DOCS_DIR, "Generate governance documentation to populate this page."
    )
    st.stop()

files = markdown_files()
if not files:
    st.info("No Markdown files were found under `docs/`.")
    st.stop()

n8n_doc = DOCS_DIR / "n8n_automation.md"
if n8n_doc.exists():
    st.success("n8n automation documentation is available: `docs/n8n_automation.md`")
else:
    st.warning("`docs/n8n_automation.md` was not found.")

file_rows = [
    {
        "document": relative_path(path),
        "size_bytes": path.stat().st_size,
        "highlight": "n8n automation" if path == n8n_doc else "",
    }
    for path in files
]
st.dataframe(file_rows, width="stretch", hide_index=True)

default_index = files.index(n8n_doc) if n8n_doc in files else 0
selected = st.selectbox(
    "Select a document to preview",
    [relative_path(path) for path in files],
    index=default_index,
)
selected_path = next(path for path in files if relative_path(path) == selected)
content = read_text_safe(selected_path)

st.subheader(relative_path(selected_path))
if content:
    st.markdown(content)
else:
    st.info("The selected document is empty or could not be read.")
