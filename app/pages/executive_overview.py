from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.config import PUBLISHED_MONITORING_DIR
from src.governance_types import DataQualityResult, PrivacyRiskResult

GOVERNANCE_HISTORY_PATH = PUBLISHED_MONITORING_DIR / "governance_history.csv"
DEFAULT_PUBLISHED_DATASET = Path("data/published/dashboard/fact_orders_dashboard.csv")


def _load_previous_snapshot() -> dict[str, float] | None:
    if not GOVERNANCE_HISTORY_PATH.exists():
        return None
    try:
        history = pd.read_csv(GOVERNANCE_HISTORY_PATH)
        if len(history) < 2:
            return None
        last = history.iloc[-2]
        return {
            "privacy_risk_score": float(last.get("privacy_risk_score", 0)),
            "data_quality_score": float(last.get("data_quality_score", 0)),
            "failed_rules_count": float(last.get("failed_rules_count", 0)),
        }
    except Exception:
        return None


def _data_freshness(path: Path = DEFAULT_PUBLISHED_DATASET) -> str | None:
    if not path.exists():
        return None
    mtime = path.stat().st_mtime
    age_hours = (datetime.now(timezone.utc).timestamp() - mtime) / 3600
    if age_hours < 1:
        return "< 1h"
    if age_hours < 24:
        return f"{int(age_hours)}h"
    days = int(age_hours / 24)
    return f"{days}d"


def render_executive_overview(
    df: pd.DataFrame,
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
    locale: Locale,
) -> None:
    is_en = locale == LOCALE_EN_US
    personal_fields = int(
        classification_df["lgpd_classification"]
        .isin(["personal_data", "sensitive_personal_data"])
        .sum()
    )
    suppressed_columns = int(
        classification_df["recommended_action"]
        .isin(["anonymize", "remove", "pseudonymize"])
        .sum()
    )
    quality_score = max(0, 100 - quality_results["failed_checks_count"] * 10)
    status = (
        (
            "Healthy"
            if quality_results["failed_checks_count"] == 0
            else "Attention Required"
        )
        if is_en
        else (
            "Saudável"
            if quality_results["failed_checks_count"] == 0
            else "Requer Atenção"
        )
    )

    prev = _load_previous_snapshot()
    risk_delta: int | None = None
    quality_delta: int | None = None
    failures_delta: int | None = None
    if prev is not None:
        risk_delta = int(risk_result["score"]) - int(prev["privacy_risk_score"])
        quality_delta = quality_score - int(prev["data_quality_score"])
        failures_delta = quality_results["failed_checks_count"] - int(
            prev["failed_rules_count"]
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total de Colunas" if not is_en else "Total Columns",
            df.shape[1],
        )
        st.metric(
            "Campos Pessoais / Personal Fields" if not is_en else "Personal Fields",
            personal_fields,
        )
    with col2:
        st.metric(
            "Score de Risco LGPD" if not is_en else "LGPD Risk Score",
            f"{risk_result['score']} / 100",
            delta=risk_delta,
            delta_color="inverse",
        )
        st.metric(
            "Score de Qualidade" if not is_en else "Data Quality Score",
            f"{quality_score} / 100",
            delta=quality_delta,
        )
    with col3:
        st.metric(
            "Falhas de Qualidade" if not is_en else "Quality Failures",
            quality_results["failed_checks_count"],
            delta=failures_delta,
            delta_color="inverse",
        )
        st.metric(
            "Status de Governança" if not is_en else "Governance Status",
            status,
        )

    st.divider()

    extra_col1, extra_col2, extra_col3 = st.columns(3)
    freshness = _data_freshness()
    with extra_col1:
        st.metric(
            "Freshness dos Dados" if not is_en else "Data Freshness",
            freshness
            if freshness
            else (
                "N/A — pipeline não executado"
                if not is_en
                else "N/A — pipeline not run"
            ),
        )
    with extra_col2:
        st.metric(
            "Colunas Suprimidas (LGPD)" if not is_en else "Suppressed Columns (LGPD)",
            suppressed_columns,
            help=(
                "Colunas com ação: anonimizar, remover ou pseudonimizar."
                if not is_en
                else "Columns with action: anonymize, remove or pseudonymize."
            ),
        )
    with extra_col3:
        sensitive_count = int(
            (
                classification_df["lgpd_classification"] == "sensitive_personal_data"
            ).sum()
        )
        st.metric(
            "Dados Sensíveis" if not is_en else "Sensitive Data Columns",
            sensitive_count,
        )

    st.subheader("Resumo Executivo" if not is_en else "Executive Summary")
    risk_level = risk_result["risk_level"]
    if is_en:
        st.write(
            f"The dataset has **{len(df):,}** rows and **{df.shape[1]}** columns. "
            f"The current LGPD risk is **{risk_level}** (score **{risk_result['score']}/100**). "
            f"Data quality score is **{quality_score}/100** with **{quality_results['failed_checks_count']}** failed checks. "
            f"**{suppressed_columns}** columns are under active LGPD protection."
        )
    else:
        st.write(
            f"O dataset possui **{len(df):,}** registros e **{df.shape[1]}** colunas. "
            f"O risco LGPD atual é **{risk_level}** (score **{risk_result['score']}/100**). "
            f"O score de qualidade é **{quality_score}/100** com **{quality_results['failed_checks_count']}** falhas. "
            f"**{suppressed_columns}** colunas estão sob proteção LGPD ativa."
        )
    if prev is None:
        st.caption(
            "Salve um snapshot na Central de Controles para habilitar comparações de tendência."
            if not is_en
            else "Save a snapshot in the Control Center to enable trend comparisons."
        )
