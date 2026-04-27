from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from streamlit_app.analytics import build_metrics
from streamlit_app.data import (
    build_app_mode,
    build_dashboard_locale,
    build_sidebar_filters,
    filter_dataframe,
    get_previous_period_df,
    load_data,
    load_monitoring_status,
    load_semantic_assets,
)
from streamlit_app.formatting import format_number, set_format_locale
from streamlit_app.i18n import tr
from streamlit_app.sections import (
    render_category_section,
    render_context_bar,
    render_executive_insights,
    render_geography_section,
    render_header,
    render_health_section,
    render_kpi_row,
    render_operations_section,
    render_semantic_section,
    render_smart_summary,
    render_temporal_section,
)
from streamlit_app.theme import apply_theme, render_story_nav

st.set_page_config(
    page_title="Governed Analytics Platform | Executive Dashboard",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    apply_theme()
    locale = build_dashboard_locale()
    set_format_locale(locale)
    st.markdown(
        "<div class='filter-note' style='margin-bottom:0.45rem;'><strong>Language:</strong> English (US)</div>"
        if locale == "en-US"
        else "<div class='filter-note' style='margin-bottom:0.45rem;'><strong>Idioma:</strong> Português (Brasil)</div>",
        unsafe_allow_html=True,
    )
    try:
        df = load_data()
    except (FileNotFoundError, ValueError) as exc:
        st.error(str(exc))
        st.stop()
    semantic_assets = load_semantic_assets()
    monitoring_status = load_monitoring_status()

    filters = build_sidebar_filters(df)
    presentation_mode = build_app_mode()
    filtered_df = filter_dataframe(df, filters)
    previous_df = get_previous_period_df(df, filters)
    if filtered_df.empty:
        st.warning("No records found for the selected filters." if locale == "en-US" else "Nenhum registro encontrado para os filtros selecionados.")
        st.stop()

    st.sidebar.caption(f"{tr('filtered_rows_caption')}: {format_number(len(filtered_df))}")
    render_header(filters, total_rows=len(df), filtered_rows=len(filtered_df))

    if presentation_mode:
        st.markdown(
            f"<div class='section-shell' style='padding:0.8rem 1rem;'><div class='section-eyebrow'>{tr('presentation_mode_title')}</div><p class='section-copy' style='margin-bottom:0;'>{tr('presentation_mode_copy')}</p></div>",
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
    elif selected_section == "Saúde":
        render_health_section(monitoring_status)
    elif selected_section == "Semântica":
        render_semantic_section(semantic_assets)
    elif selected_section == "Insights":
        render_executive_insights(filtered_df)
    elif selected_section == "Visão completa":
        st.markdown(
            f"<div class='section-shell' style='padding:0.8rem 1rem;'><div class='section-eyebrow'>{tr('guided_read_title')}</div><p class='section-copy' style='margin-bottom:0;'>{tr('guided_read_copy')}</p></div>",
            unsafe_allow_html=True,
        )
        render_temporal_section(filtered_df)
        render_category_section(filtered_df)
        render_geography_section(filtered_df, filters.geography_mode)
        render_executive_insights(filtered_df)


if __name__ == "__main__":
    main()
