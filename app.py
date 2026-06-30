from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Governed Analytics Platform",
    page_icon=":material/policy:",
    layout="wide",
)


def main() -> None:
    pages = [
        st.Page("pages/01_Overview.py", title="Overview", icon=":material/dashboard:"),
        st.Page(
            "pages/02_Data_Quality.py",
            title="Data Quality",
            icon=":material/rule:",
        ),
        st.Page(
            "pages/03_LGPD_Risk.py",
            title="LGPD Risk",
            icon=":material/security:",
        ),
        st.Page(
            "pages/04_Data_Contracts.py",
            title="Data Contracts",
            icon=":material/contract:",
        ),
        st.Page(
            "pages/05_Pipeline_Logs.py",
            title="Pipeline Logs",
            icon=":material/monitoring:",
        ),
        st.Page(
            "pages/06_n8n_Automation.py",
            title="n8n Automation",
            icon=":material/account_tree:",
        ),
        st.Page(
            "pages/07_Governance_Docs.py",
            title="Governance Docs",
            icon=":material/article:",
        ),
        st.Page(
            "pages/08_Operational_Health.py",
            title="Operational Health",
            icon=":material/vital_signs:",
        ),
    ]
    selected_page = st.navigation(pages)
    selected_page.run()


if __name__ == "__main__":
    main()
