from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.i18n import LOCALE_EN_US, Locale


def render_governance_report(report_paths: dict[str, Path], locale: Locale) -> None:
    st.subheader("Governance Report" if locale == LOCALE_EN_US else "Relatório de Governança")
    st.write(
        "Automatically generated Markdown reports:"
        if locale == LOCALE_EN_US
        else "Relatórios em Markdown gerados automaticamente:"
    )
    for name, path in report_paths.items():
        st.write(f"- **{name}**: `{path}`")
        if path.exists():
            st.code(path.read_text(encoding="utf-8")[:2000])
