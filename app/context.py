from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from app.i18n import Locale, t
from src.data_loader import DEFAULT_SAMPLE_DATASET, load_dataset
from src.data_quality import generate_data_quality_table, run_data_quality_checks
from src.governance_types import DataQualityResult, PrivacyRiskResult
from src.lgpd_classifier import classify_dataframe_columns
from src.report_generator import generate_markdown_reports
from src.risk_scoring import calculate_privacy_risk_score

DEFAULT_PUBLISHED_DATASET = Path("data/published/dashboard/fact_orders_dashboard.csv")


@dataclass(frozen=True)
class GovernanceAppContext:
    df: pd.DataFrame
    classification_df: pd.DataFrame
    quality_results: DataQualityResult
    quality_table: pd.DataFrame
    risk_result: PrivacyRiskResult
    report_paths: dict[str, Path]


def _render_data_freshness_sidebar(locale: Locale) -> None:
    is_en = locale == "en-US"
    if DEFAULT_PUBLISHED_DATASET.exists():
        import time

        mtime = DEFAULT_PUBLISHED_DATASET.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        if age_hours < 1:
            age_str = "< 1h"
        elif age_hours < 24:
            age_str = (
                f"{int(age_hours)}h atrás" if not is_en else f"{int(age_hours)}h ago"
            )
        else:
            days = int(age_hours / 24)
            age_str = f"{days}d atrás" if not is_en else f"{days}d ago"
        label = "Dados publicados:" if not is_en else "Published data:"
        st.sidebar.caption(f"{label} **{age_str}**")
    else:
        st.sidebar.caption(
            "Pipeline não executado ainda." if not is_en else "Pipeline not run yet."
        )


def load_input_dataframe(locale: Locale) -> pd.DataFrame:
    st.sidebar.header(t("data_source_header", locale))
    uploaded_file = st.sidebar.file_uploader(
        t("upload_label", locale), type=["csv", "parquet"]
    )
    use_sample = st.sidebar.toggle(t("use_sample_toggle", locale), value=True)
    _render_data_freshness_sidebar(locale)

    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix == ".parquet":
            return pd.read_parquet(uploaded_file)
        return pd.read_csv(uploaded_file)

    if use_sample:
        if DEFAULT_PUBLISHED_DATASET.exists():
            return load_dataset(DEFAULT_PUBLISHED_DATASET)
        return load_dataset(DEFAULT_SAMPLE_DATASET)
    if DEFAULT_PUBLISHED_DATASET.exists():
        return load_dataset(DEFAULT_PUBLISHED_DATASET)
    return load_dataset(DEFAULT_SAMPLE_DATASET)


@st.cache_data(show_spinner=False)
def _build_context_from_dataframe(df: pd.DataFrame) -> GovernanceAppContext:
    classification_df = classify_dataframe_columns(df)
    quality_results = run_data_quality_checks(df)
    quality_table = generate_data_quality_table(df)
    risk_result = calculate_privacy_risk_score(classification_df, total_rows=len(df))
    report_paths = generate_markdown_reports(df, docs_dir="docs")
    return GovernanceAppContext(
        df=df,
        classification_df=classification_df,
        quality_results=quality_results,
        quality_table=quality_table,
        risk_result=risk_result,
        report_paths=report_paths,
    )


def build_context(locale: Locale) -> GovernanceAppContext:
    df = load_input_dataframe(locale)
    return _build_context_from_dataframe(df)
