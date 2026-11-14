from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit.navigation.page import StreamlitPage

from app.components.cards import render_metric_cards
from app.components.ui import inject_base_styles, render_footer, render_section_title
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


def _count_critical_failures(quality_results: DataQualityResult) -> int:
    checks = quality_results.get("checks")
    if not isinstance(checks, list):
        return 0
    return sum(
        1
        for check in checks
        if str(check.get("status", "")).strip().upper() != "PASS"
        and str(check.get("severity", "")).strip().lower() == "critical"
    )


def _render_operational_readiness_section(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.subheader(
        "Production-Style Readiness"
        if is_en
        else "Prontid\u00e3o operacional simulada"
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
        else "AWS est\u00e1 documentada como arquitetura de refer\u00eancia; nenhum recurso cloud ou credencial \u00e9 inclu\u00eddo."
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
                f"- {guardrail['name']}: {guardrail['control']}"
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
    uses_persisted_governance: bool = False,
    quick_pages: dict[str, StreamlitPage] | None = None,
) -> None:
    is_en = locale == LOCALE_EN_US
    inject_base_styles()

    snapshot = governance_snapshot or (
        load_publication_governance_snapshot() if uses_persisted_governance else None
    )
    unavailable = "Unavailable" if is_en else "Indispon\u00edvel"
    missing_evidence = "No evidence" if is_en else "Sem evid\u00eancia"

    subtitle = (
        "Trusted data, verifiable governance, controlled publication."
        if is_en
        else "Dados confi\u00e1veis, governan\u00e7a verific\u00e1vel e publica\u00e7\u00e3o controlada."
    )
    st.title("GOVERNED ANALYTICS PLATFORM")
    st.caption(subtitle)

    st.markdown(
        (
            "A governed analytics platform that turns raw data into business insights "
            "while enforcing quality, privacy, and auditable publication decisions."
        )
        if is_en
        else (
            "Uma plataforma de analytics governada que transforma dados brutos em insights "
            "de neg\u00f3cio, com qualidade, privacidade e decis\u00f5es de publica\u00e7\u00e3o audit\u00e1veis."
        )
    )
    st.caption(
        (
            "The dataset and workflows shown here are demonstrative and do not represent a live business operation."
        )
        if is_en
        else (
            "Os dados e fluxos apresentados s\u00e3o demonstrativos e n\u00e3o representam uma opera\u00e7\u00e3o empresarial em produ\u00e7\u00e3o."
        )
    )

    render_section_title("Executive Overview")
    intent_col1, intent_col2, intent_col3 = st.columns(3)
    with intent_col1:
        st.info(
            "Problem: unreliable data in analytics delivery"
            if is_en
            else "Problema: dados pouco confi\u00e1veis no consumo anal\u00edtico"
        )
    with intent_col2:
        st.info(
            "Control: quality + privacy checks + publication gate"
            if is_en
            else "Controle: qualidade + privacidade + publication gate"
        )
    with intent_col3:
        st.success(
            "Evidence: persisted decisions and governance artifacts"
            if is_en
            else "Evid\u00eancia: decis\u00f5es e artefatos de governan\u00e7a"
        )

    if business_page is not None or governance_page is not None or quick_pages:
        render_section_title("Quick access" if is_en else "Acesso r\u00e1pido")
        links: list[tuple[str, StreamlitPage | None, str]] = [
            (
                "Publication Gate" if is_en else "Publication Gate",
                governance_page,
                ":material/policy:",
            ),
            (
                "Business KPIs" if is_en else "Indicadores anal\u00edticos",
                business_page,
                ":material/insights:",
            ),
            (
                "Data Quality" if is_en else "Data Quality",
                (quick_pages or {}).get("data_quality"),
                ":material/check_circle:",
            ),
            (
                "Contracts & Catalog" if is_en else "Contratos e Cat\u00e1logo",
                (quick_pages or {}).get("data_catalog"),
                ":material/table_view:",
            ),
            (
                "LGPD & Privacy" if is_en else "LGPD e Privacidade",
                (quick_pages or {}).get("lgpd_privacy"),
                ":material/policy:",
            ),
            (
                "Control Center" if is_en else "Central de Controles",
                (quick_pages or {}).get("control_center"),
                ":material/admin_panel_settings:",
            ),
        ]
        links = [link for link in links if link[1] is not None]
        for start in range(0, len(links), 3):
            row = links[start : start + 3]
            cols = st.columns(len(row))
            for idx, (label, page, icon) in enumerate(row):
                with cols[idx]:
                    if page is None:
                        continue
                    st.page_link(page, label=label, icon=icon, use_container_width=True)

    prev = _load_previous_snapshot()

    quality_score = max(0, 100 - quality_results["failed_checks_count"] * 10)
    freshness = _data_freshness()
    critical_failures = _count_critical_failures(quality_results)

    risk_delta: int | None = None
    quality_delta: int | None = None
    failures_delta: int | None = None
    if prev is not None:
        risk_delta = int(risk_result["score"]) - int(prev["privacy_risk_score"])
        quality_delta = quality_score - int(prev["data_quality_score"])
        failures_delta = quality_results["failed_checks_count"] - int(
            prev["failed_rules_count"]
        )

    publication_status = unavailable if snapshot is None else snapshot.historical_decision
    contracts_status = unavailable
    if snapshot is not None:
        contracts_status = (
            snapshot.schema.display if snapshot.schema.total > 0 else missing_evidence
        )

    render_section_title("Governance snapshot" if is_en else "Snapshot de governan\u00e7a")
    render_metric_cards(
        [
            {
                "label": (
                    "Governed records" if snapshot is not None else "Analyzed records"
                )
                if is_en
                else (
                    "Registros governados"
                    if snapshot is not None
                    else "Registros analisados"
                ),
                "value": f"{len(df):,}",
            },
            {
                "label": "Publication Gate" if is_en else "Publication Gate",
                "value": publication_status,
            },
            {
                "label": "Data Quality Score" if is_en else "Data Quality Score",
                "value": f"{quality_score} / 100",
                "delta": (f"{quality_delta:+d}" if quality_delta is not None else None),
            },
            {
                "label": "Privacy Risk Score" if is_en else "Privacy Risk Score",
                "value": f"{risk_result['score']} / 100",
                "delta": (f"{risk_delta:+d}" if risk_delta is not None else None),
            },
            {
                "label": "Data freshness" if is_en else "Freshness dos dados",
                "value": freshness if freshness else unavailable,
            },
            {
                "label": "Critical checks" if is_en else "Checks cr\u00edticos",
                "value": str(critical_failures),
                "delta": (f"{failures_delta:+d}" if failures_delta is not None else None),
            },
            {
                "label": "Data contracts" if is_en else "Contratos de dados",
                "value": contracts_status,
            },
        ],
        max_columns=3,
    )
    st.caption(
        (
            "Sources: runtime checks (quality/privacy) plus persisted publication evidence when available."
        )
        if is_en
        else (
            "Fontes: checagens em runtime (qualidade/privacidade) e evid\u00eancias persistidas de publica\u00e7\u00e3o quando dispon\u00edveis."
        )
    )

    render_section_title(
        "Technical evidence (historical)" if is_en else "Evid\u00eancias t\u00e9cnicas (hist\u00f3rico)"
    )
    render_metric_cards(
        [
            {
                "label": "Passing tests" if is_en else "Testes aprovados",
                "value": "1,353" if is_en else "1.353",
            },
            {
                "label": "Coverage (src + app)" if is_en else "Cobertura (src + app)",
                "value": "92%",
            },
            {
                "label": "Failures / errors / skips" if is_en else "Falhas / erros / skips",
                "value": "0 / 0 / 0",
            },
            {
                "label": "Local validation" if is_en else "Valida\u00e7\u00e3o local",
                "value": "13 Nov 2026" if is_en else "13/11/2026",
            },
        ],
        max_columns=4,
    )
    st.caption(
        (
            "Documented evidence from Checkpoint 16C (local run). Not a live CI/status indicator."
        )
        if is_en
        else (
            "Evid\u00eancias documentadas do Checkpoint 16C (execu\u00e7\u00e3o local). N\u00e3o representa status atual de CI."
        )
    )

    st.markdown(
        "[GitHub](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform)"
        " . [Architecture](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/blob/main/docs/architecture/architecture.md)"
        " . [Case study](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/blob/main/docs/executive/case_study.md)"
        " . [Executive documentation](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/blob/main/docs/executive/executive_summary.md)"
    )

    if snapshot is None:
        st.warning(
            (
                "Persisted evidence belongs to fact_orders_dashboard and does not validate uploaded or sample data."
            )
            if is_en
            else (
                "As evid\u00eancias persistidas pertencem a fact_orders_dashboard e n\u00e3o validam dados enviados ou de amostra."
            )
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
    sensitive_count = int(
        (classification_df["lgpd_classification"] == "sensitive_personal_data").sum()
    )
    status = (
        ("Healthy" if quality_results["failed_checks_count"] == 0 else "Attention Required")
        if is_en
        else (
            "Saud\u00e1vel"
            if quality_results["failed_checks_count"] == 0
            else "Requer aten\u00e7\u00e3o"
        )
    )

    st.divider()
    with st.expander(
        "Detailed governance metrics" if is_en else "M\u00e9tricas detalhadas de governan\u00e7a",
        expanded=False,
    ):
        st.caption(
            "Diagnostic indicators from the demonstration environment."
            if is_en
            else "Indicadores diagn\u00f3sticos do ambiente demonstrativo."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Columns" if is_en else "Total de colunas", df.shape[1])
            st.metric("Personal Fields" if is_en else "Campos pessoais", personal_fields)
        with col2:
            st.metric(
                "LGPD Risk Score" if is_en else "Score de risco LGPD",
                f"{risk_result['score']} / 100",
                delta=risk_delta,
                delta_color="inverse",
            )
            st.metric(
                "Data Quality Score" if is_en else "Score de qualidade",
                f"{quality_score} / 100",
                delta=quality_delta,
            )
        with col3:
            st.metric(
                "Quality Failures" if is_en else "Falhas de qualidade",
                quality_results["failed_checks_count"],
                delta=failures_delta,
                delta_color="inverse",
            )
            st.metric("Governance Status" if is_en else "Status de governan\u00e7a", status)

        extra_col1, extra_col2, extra_col3 = st.columns(3)
        with extra_col1:
            st.metric(
                "Data Freshness" if is_en else "Freshness dos dados",
                freshness
                if freshness
                else (
                    "N/A - pipeline not run" if is_en else "N/A - pipeline n\u00e3o executado"
                ),
            )
        with extra_col2:
            st.metric(
                "Suppressed Columns (LGPD)" if is_en else "Colunas suprimidas (LGPD)",
                suppressed_columns,
                help=(
                    "Columns with action: anonymize, remove or pseudonymize."
                    if is_en
                    else "Colunas com a\u00e7\u00e3o: anonimizar, remover ou pseudonimizar."
                ),
            )
        with extra_col3:
            st.metric(
                "Sensitive Data Columns" if is_en else "Dados sens\u00edveis",
                sensitive_count,
            )
        if duckdb_version is not None:
            st.caption(f"DuckDB: {duckdb_version}")

    st.subheader("Executive Summary" if is_en else "Resumo Executivo")
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
            "O projeto demonstra uma plataforma de analytics governada com "
            f"**{len(df):,}** registros e **{df.shape[1]}** colunas, pipeline de "
            "transforma\u00e7\u00e3o, controles de qualidade e privacidade, governan\u00e7a de "
            "publica\u00e7\u00e3o e camada anal\u00edtica para gera\u00e7\u00e3o de insights. As avalia\u00e7\u00f5es "
            "t\u00e9cnicas detalhadas permanecem dispon\u00edveis nas p\u00e1ginas de governan\u00e7a "
            "e qualidade."
        )
    if prev is None:
        st.caption(
            "Save a snapshot in the Control Center to enable trend comparisons."
            if is_en
            else "Salve um snapshot na Central de Controles para habilitar compara\u00e7\u00f5es de tend\u00eancia."
        )

    st.divider()
    _render_operational_readiness_section(locale)

    render_footer(locale=str(locale))

