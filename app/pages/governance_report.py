from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.i18n import LOCALE_EN_US, Locale


def render_governance_report(report_paths: dict[str, Path], locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader("Governance Report" if is_en else "Relatório de Governança")
    st.write(
        "Automatically generated Markdown reports:"
        if is_en
        else "Relatórios em Markdown gerados automaticamente:"
    )

    existing = {name: path for name, path in report_paths.items() if path.exists()}
    missing = {name: path for name, path in report_paths.items() if not path.exists()}

    if not existing and not missing:
        st.info(
            "No reports found. Run the pipeline to generate governance reports."
            if is_en
            else "Nenhum relatório encontrado. Execute o pipeline para gerar os relatórios de governança."
        )
        return

    for name, path in existing.items():
        icon = ":material/description:"
        with st.expander(f"{icon} {name}", expanded=False):
            st.caption(f"`{path}`")
            content = path.read_text(encoding="utf-8")
            tab_rendered, tab_raw = st.tabs(["Renderizado / Rendered", "Markdown Raw"])
            with tab_rendered:
                st.markdown(content)
            with tab_raw:
                st.code(content, language="markdown")

    if missing:
        st.divider()
        st.caption(
            f"{'Relatórios não encontrados' if not is_en else 'Reports not found'} "
            f"({'execute o pipeline' if not is_en else 'run the pipeline'}):"
        )
        for name, path in missing.items():
            st.write(f"- **{name}**: `{path}`")
