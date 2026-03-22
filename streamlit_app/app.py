from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from streamlit_app.analytics import build_metrics
from streamlit_app.data import build_app_mode, build_sidebar_filters, filter_dataframe, get_previous_period_df, load_data
from streamlit_app.formatting import format_number
from streamlit_app.sections import (
    render_category_section,
    render_context_bar,
    render_executive_insights,
    render_geography_section,
    render_header,
    render_kpi_row,
    render_operations_section,
    render_smart_summary,
    render_support_tables,
    render_temporal_section,
)
from streamlit_app.theme import apply_theme, render_story_nav


st.set_page_config(
    page_title="samuelmaia_DDF_032026 | Executive Commerce Analytics",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    apply_theme()
    try:
        df = load_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    filters = build_sidebar_filters(df)
    presentation_mode = build_app_mode()
    filtered_df = filter_dataframe(df, filters)
    previous_df = get_previous_period_df(df, filters)
    if filtered_df.empty:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")
        st.stop()

    st.sidebar.caption(f"Registros filtrados: {format_number(len(filtered_df))}")
    render_header(filters)

    if presentation_mode:
        st.markdown(
            "<div class='section-shell' style='padding:0.8rem 1rem;'><div class='section-eyebrow'>Modo apresentação</div><p class='section-copy' style='margin-bottom:0;'>A leitura foi reduzida ao fluxo executivo principal: KPIs, tendência, categorias, performance regional e síntese final.</p></div>",
            unsafe_allow_html=True,
        )
        render_kpi_row(build_metrics(filtered_df, previous_df))
        st.markdown("<div style='height:0.95rem;'></div>", unsafe_allow_html=True)
        render_temporal_section(filtered_df)
        render_category_section(filtered_df)
        render_geography_section(filtered_df, filters.geography_mode)
        render_executive_insights(filtered_df)
        return

    selected_section = render_story_nav()

    if selected_section in {"Visão completa", "Contexto"}:
        render_context_bar(filtered_df, filters)
        st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)
        render_smart_summary(filtered_df)

    if selected_section in {"Visão completa", "KPIs"}:
        render_kpi_row(build_metrics(filtered_df, previous_df))
        st.markdown("<div style='height:0.95rem;'></div>", unsafe_allow_html=True)

    if selected_section == "Tempo":
        render_temporal_section(filtered_df)
    elif selected_section == "Categorias":
        render_category_section(filtered_df)
    elif selected_section == "Regional":
        render_geography_section(filtered_df, filters.geography_mode)
    elif selected_section == "Operação":
        render_operations_section(filtered_df)
    elif selected_section == "Insights":
        render_executive_insights(filtered_df)
    elif selected_section == "Visão completa":
        render_temporal_section(filtered_df)
        render_category_section(filtered_df)
        render_geography_section(filtered_df, filters.geography_mode)
        render_operations_section(filtered_df)
        render_executive_insights(filtered_df)

    if selected_section == "Visão completa":
        render_support_tables(filtered_df)


if __name__ == "__main__":
    main()
