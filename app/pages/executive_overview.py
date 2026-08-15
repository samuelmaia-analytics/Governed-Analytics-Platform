from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit.navigation.page import StreamlitPage

from app.i18n import LOCALE_EN_US, Locale
from app.pages.publication_governance import (
    PublicationGovernanceSnapshot,
    load_publication_governance_snapshot,
)
from src.cloud_reference import summarize_cost_controls
from src.config import PUBLISHED_MONITORING_DIR
from src.data_lake_layers import summarize_layer_status
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


def _render_operational_readiness_section(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader(
        "Production-Style Readiness"
        if is_en
        else "Prontidão operacional simulada"
    )

    layer_status = summarize_layer_status()
    ready_layers = sum(1 for layer in layer_status if layer["ready"])
    cost_summary = summarize_cost_controls()
    guardrail_count = cost_summary["guardrail_count"]
    guardrails = cost_summary["guardrails"]
    if not isinstance(guardrail_count, int):
        raise TypeError("guardrail_count must be an integer")
    if not isinstance(guardrails, list):
        raise TypeError("guardrails must be a list")

    st.caption(
        "AWS is documented as a reference architecture; no cloud resources or credentials are bundled."
        if is_en
        else "AWS esta documentada como arquitetura de referencia; nenhum recurso cloud ou credencial e incluido."
    )

    with st.expander(
        "Infrastructure, layers, and cost controls"
        if is_en
        else "Infraestrutura, camadas e controles de custo"
    ):
        readiness_col1, readiness_col2, readiness_col3 = st.columns(3)
        with readiness_col1:
            st.metric(
                "Data Lake Layers" if is_en else "Camadas do Data Lake",
                f"{ready_layers} / {len(layer_status)}",
            )
        with readiness_col2:
            st.metric(
                "Cost Guardrails" if is_en else "Guardrails de custo",
                guardrail_count,
            )
        with readiness_col3:
            st.metric(
                "Cloud Status" if is_en else "Status cloud",
                "Reference only"
                if not cost_summary["is_provisioned"]
                else "Provisioned",
            )
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "layer": layer["layer"],
                        "ready": layer["ready"],
                        "paths": layer["path_count"],
                        "owner_role": layer["owner_role"],
                        "sensitivity": layer["sensitivity_default"],
                    }
                    for layer in layer_status
                ]
            ),
            width="stretch",
        )
        st.markdown(
            "\n".join(
                f"- `{guardrail['name']}`: {guardrail['control']}"
                for guardrail in guardrails
            )
        )


def render_executive_overview(
    df: pd.DataFrame,
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
    locale: Locale,
    *,
    business_page: StreamlitPage | None = None,
    governance_page: StreamlitPage | None = None,
    governance_snapshot: PublicationGovernanceSnapshot | None = None,
    duckdb_version: str | None = None,
) -> None:
    is_en = locale == LOCALE_EN_US
    snapshot = governance_snapshot or load_publication_governance_snapshot()

    historical_decision = snapshot.historical_decision.strip()
    if historical_decision.casefold() in {"", "none", "unavailable"}:
        historical_decision = (
            "Demonstration evidence" if is_en else "Evidência demonstrativa"
        )
    privacy_summary = (
        snapshot.privacy.display
        if snapshot.privacy.total > 0
        else "Controls demonstrated"
        if is_en
        else "Controles demonstrados"
    )
    validation_summaries: list[str] = []
    if snapshot.quality.total > 0:
        validation_summaries.append(
            f"Quality {snapshot.quality.passed}/{snapshot.quality.total}"
            if is_en
            else f"Qualidade {snapshot.quality.passed}/{snapshot.quality.total}"
        )
    if snapshot.monitoring.total > 0:
        validation_summaries.append(
            f"Monitoring {snapshot.monitoring.passed}/{snapshot.monitoring.total}"
            if is_en
            else f"Monitoramento {snapshot.monitoring.passed}/{snapshot.monitoring.total}"
        )
    validation_summary = " · ".join(validation_summaries) or (
        "Validations demonstrated" if is_en else "Validações demonstradas"
    )

    st.title("Governed Analytics Platform")
    st.caption("Projeto de portfólio profissional")
    st.markdown(
        "Uma plataforma analítica end-to-end que transforma dados brutos em "
        "insights de negócio com qualidade, privacidade e decisões de publicação "
        "auditáveis."
    )
    st.caption(
        "Os dados e fluxos apresentados são utilizados para fins demonstrativos "
        "e não representam uma operação empresarial em produção."
    )

    primary_col1, primary_col2, primary_col3, primary_col4 = st.columns(4)
    primary_col1.metric("Registros governados", f"{len(df):,}")
    primary_col2.metric("Decisão oficial de publicação", historical_decision)
    primary_col3.metric("Privacy controls aprovados", privacy_summary)
    primary_col4.metric(
        "Quality/monitoring status",
        validation_summary,
    )

    st.markdown("**Fluxo de valor governado**")
    flow_columns = st.columns(4)
    flow_columns[0].info("Raw Data")
    flow_columns[1].info("Quality & Privacy Controls")
    flow_columns[2].info("Publication Gate")
    flow_columns[3].success("Trusted Analytics")
    st.caption(
        "Raw Data → Quality & Privacy Controls → Publication Gate → Trusted Analytics"
    )

    if business_page is not None and governance_page is not None:
        cta_col1, cta_col2 = st.columns(2)
        cta_col1.page_link(
            business_page,
            label="Explore Business Insights",
            icon=":material/insights:",
            width="stretch",
        )
        cta_col2.page_link(
            governance_page,
            label="View Governance Decision",
            icon=":material/policy:",
            width="stretch",
        )

    st.markdown(
        "[GitHub](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform)"
        " · [Architecture](https://github.com/samuelmaia-analytics/"
        "Governed-Analytics-Platform/blob/main/docs/architecture/architecture.md)"
        " · [Case study](https://github.com/samuelmaia-analytics/"
        "Governed-Analytics-Platform/blob/main/docs/executive/case_study.md)"
        " · [Executive documentation](https://github.com/samuelmaia-analytics/"
        "Governed-Analytics-Platform/blob/main/docs/executive/executive_summary.md)"
    )
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

    freshness = _data_freshness()
    sensitive_count = int(
        (classification_df["lgpd_classification"] == "sensitive_personal_data").sum()
    )

    st.divider()
    with st.expander(
        "Detailed governance metrics"
        if is_en
        else "Métricas detalhadas de governança",
        expanded=False,
    ):
        st.caption(
            "Diagnostic indicators from the demonstration environment."
            if is_en
            else "Indicadores diagnósticos do ambiente demonstrativo."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total de Colunas" if not is_en else "Total Columns",
                df.shape[1],
            )
            st.metric(
                "Campos Pessoais" if not is_en else "Personal Fields",
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

        extra_col1, extra_col2, extra_col3 = st.columns(3)
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
                "Colunas Suprimidas (LGPD)"
                if not is_en
                else "Suppressed Columns (LGPD)",
                suppressed_columns,
                help=(
                    "Colunas com ação: anonimizar, remover ou pseudonimizar."
                    if not is_en
                    else "Columns with action: anonymize, remove or pseudonymize."
                ),
            )
        with extra_col3:
            st.metric(
                "Dados Sensíveis" if not is_en else "Sensitive Data Columns",
                sensitive_count,
            )
        if duckdb_version is not None:
            st.caption(f"DuckDB: {duckdb_version}")

    st.subheader("Resumo Executivo" if not is_en else "Executive Summary")
    if is_en:
        st.write(
            f"This project demonstrates a governed analytics platform across "
            f"**{len(df):,}** records and **{df.shape[1]}** columns, with a "
            "transformation pipeline, data quality and privacy controls, publication "
            "governance, and an analytics layer for insights. Detailed technical "
            "evaluations remain available on the governance and quality pages."
        )
    else:
        st.write(
            "O projeto demonstra uma plataforma analítica governada com "
            f"**{len(df):,}** registros e **{df.shape[1]}** colunas, pipeline de "
            "transformação, controles de qualidade e privacidade, governança de "
            "publicação e camada analítica para geração de insights. As avaliações "
            "técnicas detalhadas permanecem disponíveis nas páginas de governança "
            "e qualidade."
        )
    if prev is None:
        st.caption(
            "Salve um snapshot na Central de Controles para habilitar comparações de tendência."
            if not is_en
            else "Save a snapshot in the Control Center to enable trend comparisons."
        )

    st.divider()
    _render_operational_readiness_section(locale)
