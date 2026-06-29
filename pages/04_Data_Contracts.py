from __future__ import annotations

import streamlit as st

from pages._shared import (
    BUSINESS_RULE_RESULTS_PATH,
    CONTRACTS_DIR,
    SCHEMA_CONTRACT_RESULTS_PATH,
    count_statuses,
    read_csv_safe,
    relative_path,
    render_file_warning,
)

st.set_page_config(page_title="Data Contracts | Governed Analytics", layout="wide")

st.title("Data Contracts")
st.caption("Schema contract and business rule validation evidence.")

schema_df = read_csv_safe(SCHEMA_CONTRACT_RESULTS_PATH)
business_df = read_csv_safe(BUSINESS_RULE_RESULTS_PATH)

st.subheader("Schema contract checks")
if schema_df.empty:
    render_file_warning(
        SCHEMA_CONTRACT_RESULTS_PATH,
        "Run the contracts step in the pipeline to generate schema validation results.",
    )
else:
    counts = count_statuses(schema_df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Checks", len(schema_df))
    col2.metric("Passed", counts.get("PASS", 0))
    col3.metric("Failed", counts.get("FAIL", 0))
    st.dataframe(schema_df, width="stretch", hide_index=True)

st.subheader("Business rule checks")
if business_df.empty:
    render_file_warning(
        BUSINESS_RULE_RESULTS_PATH,
        "Run the business rules step to generate rule validation results.",
    )
else:
    counts = count_statuses(business_df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Rules", len(business_df))
    col2.metric("Passed", counts.get("PASS", 0))
    col3.metric("Failed", counts.get("FAIL", 0))
    st.dataframe(business_df, width="stretch", hide_index=True)

st.subheader("Versioned contract files")
if not CONTRACTS_DIR.exists():
    render_file_warning(CONTRACTS_DIR, "No contract directory was found.")
else:
    contract_files = sorted(
        [
            path
            for path in CONTRACTS_DIR.rglob("*")
            if path.suffix.lower() in {".json", ".yml", ".yaml"}
        ]
    )
    if not contract_files:
        st.info("No JSON/YAML contract files were found.")
    else:
        st.dataframe(
            [
                {
                    "contract_file": relative_path(path),
                    "size_bytes": path.stat().st_size,
                }
                for path in contract_files
            ],
            width="stretch",
            hide_index=True,
        )
