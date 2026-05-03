from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.governance_types import DataQualityResult


def render_data_quality(quality_results: DataQualityResult, quality_table: pd.DataFrame, locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader("Data Quality" if locale == LOCALE_EN_US else "Qualidade de Dados")
    failed_checks_count = int(quality_results["failed_checks_count"])
    quality_score = max(0, 100 - failed_checks_count * 10)

    pass_count = int((quality_table["status"] == "PASS").sum()) if "status" in quality_table.columns else 0
    fail_count = int((quality_table["status"] == "FAIL").sum()) if "status" in quality_table.columns else 0

    high_fail_count = 0
    medium_fail_count = 0
    if {"status", "severity"}.issubset(quality_table.columns):
        failed_df = quality_table[quality_table["status"] == "FAIL"]
        high_fail_count = int((failed_df["severity"] == "high").sum())
        medium_fail_count = int((failed_df["severity"] == "medium").sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows" if locale == LOCALE_EN_US else "Total de Linhas", str(quality_results["total_rows"]))
    with col2:
        st.metric("Total Columns" if locale == LOCALE_EN_US else "Total de Colunas", str(quality_results["total_columns"]))
    with col3:
        st.metric("Failed Checks" if locale == LOCALE_EN_US else "Checks com Falha", str(failed_checks_count))
    with col4:
        st.metric("Data Quality Score", f"{quality_score} / 100")

    col5, col6 = st.columns(2)
    with col5:
        st.metric("PASS vs FAIL", f"{pass_count} / {fail_count}")
    with col6:
        st.metric("Severity (high / medium)", f"{high_fail_count} / {medium_fail_count}")

    null_profile = pd.DataFrame(
        list(quality_results["null_pct_by_column"].items()),
        columns=["column_name", "null_pct"],
    ).sort_values("null_pct", ascending=False)
    if not null_profile.empty:
        st.bar_chart(null_profile.set_index("column_name").head(20))

    status_df = quality_table["status"].value_counts().reset_index()
    status_df.columns = ["status", "count"]
    st.bar_chart(status_df.set_index("status"))

    st.markdown("**Critical Failed Checks**" if is_en else "**Checks Críticos com Falha**")
    if {"status", "severity"}.issubset(quality_table.columns):
        critical_failed = quality_table[
            (quality_table["status"] == "FAIL")
            & (quality_table["severity"].isin(["high", "medium"]))
        ]
        if critical_failed.empty:
            st.success(
                "No high/medium critical failures found."
                if is_en
                else "Nenhuma falha crítica high/medium encontrada."
            )
        else:
            st.dataframe(critical_failed, width="stretch")

    if high_fail_count > 0:
        st.error("Blocked" if is_en else "Bloqueado")
    elif medium_fail_count > 0 or fail_count > 0:
        st.warning("Needs Review" if is_en else "Requer Revisão")
    else:
        st.success("Trusted" if is_en else "Confiável")

    st.dataframe(quality_table, width="stretch")
