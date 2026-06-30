from __future__ import annotations

import pandas as pd
import streamlit as st

from pages._shared import (
    DATA_CLASSIFICATION_PATH,
    PRIVACY_RISK_PATH,
    PUBLICATION_DECISION_PATH,
    read_csv_safe,
    read_first_json,
    relative_path,
    render_file_warning,
)

st.set_page_config(page_title="LGPD Risk | Governed Analytics", layout="wide")

st.title("LGPD Risk")
st.caption(
    "Classification inventory and privacy risk scoring from generated artifacts."
)

classification_df = read_csv_safe(DATA_CLASSIFICATION_PATH)
risk_payload, risk_source = read_first_json([PRIVACY_RISK_PATH, PUBLICATION_DECISION_PATH])

if risk_payload:
    if risk_source and risk_source != PRIVACY_RISK_PATH:
        st.info(
            "The runtime privacy risk artifact was not found. Showing the "
            f"versioned publication decision from `{relative_path(risk_source)}`."
        )

    col1, col2, col3 = st.columns(3)
    privacy_score = risk_payload.get("score", risk_payload.get("privacy_risk_score", "N/A"))
    risk_level = risk_payload.get("risk_level", risk_payload.get("status", "N/A"))
    col1.metric("Privacy risk score", privacy_score)
    col2.metric("Risk / publication status", str(risk_level).upper())
    col3.metric(
        "Publication recommendation",
        str(risk_payload.get("publication_recommendation", "N/A")).upper(),
    )

    if risk_payload.get("summary"):
        st.info(str(risk_payload["summary"]))
    elif risk_payload.get("decision_reason"):
        st.info(str(risk_payload["decision_reason"]))

    components = (
        risk_payload.get("score_components") or risk_payload.get("components") or {}
    )
    if components:
        component_df = pd.DataFrame(
            [{"component": key, "points": value} for key, value in components.items()]
        )
        st.subheader("Score components")
        st.dataframe(component_df, width="stretch", hide_index=True)

    recommendations = risk_payload.get("recommendations", [])
    if recommendations:
        st.subheader("Recommendations")
        for recommendation in recommendations:
            st.write(f"- {recommendation}")
else:
    render_file_warning(
        PRIVACY_RISK_PATH,
        "Run `python scripts/run_privacy_risk_score.py` to generate the risk artifact.",
    )

st.subheader("LGPD classification")
if classification_df.empty:
    render_file_warning(
        DATA_CLASSIFICATION_PATH,
        "Run the classification step to generate the LGPD inventory.",
    )
else:
    rename_map = {
        "column": "field",
        "classification": "category",
        "risk_level": "risk",
    }
    display_df = classification_df.rename(columns=rename_map)
    expected_cols = [
        col
        for col in [
            "asset",
            "field",
            "category",
            "risk",
            "published_action",
            "publication_allowed",
        ]
        if col in display_df.columns
    ]
    st.dataframe(
        display_df[expected_cols] if expected_cols else display_df,
        width="stretch",
        hide_index=True,
    )

    if "risk" in display_df.columns:
        risk_counts = display_df["risk"].fillna("unknown").value_counts().reset_index()
        risk_counts.columns = ["risk", "count"]
        st.bar_chart(risk_counts.set_index("risk"))
