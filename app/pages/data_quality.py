from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.governance_types import DataQualityResult


def render_data_quality(quality_results: DataQualityResult, quality_table: pd.DataFrame, locale: Locale) -> None:
    st.subheader("Data Quality" if locale == LOCALE_EN_US else "Qualidade de Dados")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows" if locale == LOCALE_EN_US else "Total de Linhas", str(quality_results["total_rows"]))
    with col2:
        st.metric("Total Columns" if locale == LOCALE_EN_US else "Total de Colunas", str(quality_results["total_columns"]))
    with col3:
        st.metric("Failed Checks" if locale == LOCALE_EN_US else "Checks com Falha", str(quality_results["failed_checks_count"]))

    null_profile = pd.DataFrame(
        list(quality_results["null_pct_by_column"].items()),
        columns=["column_name", "null_pct"],
    ).sort_values("null_pct", ascending=False)
    if not null_profile.empty:
        st.bar_chart(null_profile.set_index("column_name").head(20))

    status_df = quality_table["status"].value_counts().reset_index()
    status_df.columns = ["status", "count"]
    st.bar_chart(status_df.set_index("status"))
    st.dataframe(quality_table, width="stretch")
