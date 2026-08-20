from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.config import PUBLISHED_MONITORING_DIR
from src.governance_history import append_governance_history
from src.governance_types import DataQualityResult, PrivacyRiskResult
from src.publication_gate import (
    PublicationReadinessDecision,
    evaluate_publication_readiness,
)
from src.schema_contracts import RESULTS_PATH as SCHEMA_CONTRACT_RESULTS_PATH

GOVERNANCE_HISTORY_PATH = PUBLISHED_MONITORING_DIR / "governance_history.csv"
GOVERNANCE_LAB_NOTICE = (
    "Interactive diagnostic environment. This page does not represent the "
    "authoritative publication decision."
)
PUBLISHED_MONITORING_RESULTS_PATH = (
    PUBLISHED_MONITORING_DIR / "published_layer_monitoring.csv"
)

_STATUS_LABELS_PT_BR = {
    "Approved": "Aprovado",
    "Needs Review": "Requer revisão",
    "Blocked": "Bloqueado",
}
_SEVERITY_LABELS_PT_BR = {
    "Low": "Baixa",
    "Medium": "Média",
    "High": "Alta",
    "Critical": "Crítica",
    "low": "Baixa",
    "medium": "Média",
    "high": "Alta",
    "critical": "Crítica",
}
_CLASSIFICATION_LABELS_PT_BR = {
    "non_personal": "Não pessoal",
    "indirect_identifier": "Identificador indireto",
    "personal_data": "Dado pessoal",
    "sensitive_personal_data": "Dado pessoal sensível",
}
_ACTION_LABELS_PT_BR = {
    "keep": "Manter",
    "review": "Revisar",
    "mask": "Mascarar",
    "anonymize": "Anonimizar",
    "remove": "Remover",
}
_CHECK_STATUS_LABELS_PT_BR = {
    "PASS": "Aprovado no check",
    "FAIL": "Reprovado no check",
}


def _presentation_label(
    value: object, labels: dict[str, str], *, is_en: bool
) -> str:
    technical_value = str(value)
    return technical_value if is_en else labels.get(technical_value, technical_value)


def _governance_status(privacy_level: str, failed_checks: int) -> str:
    if privacy_level == "high":
        return "Blocked"
    if privacy_level == "medium" or failed_checks > 0:
        return "Needs Review"
    return "Approved"


def _data_quality_score(quality_results: DataQualityResult) -> int:
    return max(0, 100 - quality_results["failed_checks_count"] * 10)


def _load_schema_contract_status() -> tuple[Literal["passed", "failed"], str | None]:
    if not SCHEMA_CONTRACT_RESULTS_PATH.exists():
        return "passed", "Schema contract results file not found; assumed 'passed'."
    try:
        checks_df = pd.read_csv(SCHEMA_CONTRACT_RESULTS_PATH)
    except Exception:
        return (
            "passed",
            "Schema contract results could not be parsed; assumed 'passed'.",
        )
    if checks_df.empty or "status" not in checks_df.columns:
        return "passed", "Schema contract results are empty/invalid; assumed 'passed'."
    has_failures = checks_df["status"].astype(str).str.upper().eq("FAIL").any()
    return ("failed", None) if has_failures else ("passed", None)


def _load_freshness_status() -> tuple[Literal["fresh", "warning", "stale"], str | None]:
    if not PUBLISHED_MONITORING_RESULTS_PATH.exists():
        return "fresh", "Published monitoring file not found; assumed 'fresh'."
    try:
        checks_df = pd.read_csv(PUBLISHED_MONITORING_RESULTS_PATH)
    except Exception:
        return (
            "fresh",
            "Published monitoring file could not be parsed; assumed 'fresh'.",
        )
    if checks_df.empty or "check_name" not in checks_df.columns:
        return (
            "fresh",
            "Published monitoring checks are empty/invalid; assumed 'fresh'.",
        )

    freshness_rows = checks_df[
        checks_df["check_name"].astype(str) == "published_file_freshness_hours"
    ]
    if freshness_rows.empty:
        return (
            "fresh",
            "Freshness check not found in monitoring results; assumed 'fresh'.",
        )

    freshness_row = freshness_rows.iloc[-1]
    status = str(freshness_row.get("status", "")).upper()
    if status == "PASS":
        return "fresh", None

    metric_value = pd.to_numeric(freshness_row.get("metric_value"), errors="coerce")
    threshold = pd.to_numeric(freshness_row.get("threshold"), errors="coerce")
    if (
        pd.notna(metric_value)
        and pd.notna(threshold)
        and float(metric_value) <= float(threshold) * 1.5
    ):
        return "warning", None
    return "stale", None


def _evaluate_publication_gate(
    *,
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
) -> tuple[PublicationReadinessDecision, list[str]]:
    """Evaluate publication gate with explicit fallbacks for unavailable signals."""
    fallback_notes: list[str] = []

    checks = quality_results.get("checks", [])
    if checks and all(
        isinstance(check, dict) and {"status", "severity"}.issubset(check.keys())
        for check in checks
    ):
        critical_rule_failures = int(
            sum(
                1
                for check in checks
                if str(check.get("status", "")).upper() == "FAIL"
                and str(check.get("severity", "")).lower() in {"high", "critical"}
            )
        )
    else:
        critical_rule_failures = int(quality_results["failed_checks_count"])
        fallback_notes.append(
            "Critical rule failures fallback to total failed checks (missing check severity metadata)."
        )

    schema_contract_status, schema_note = _load_schema_contract_status()
    if schema_note:
        fallback_notes.append(schema_note)

    freshness_status, freshness_note = _load_freshness_status()
    if freshness_note:
        fallback_notes.append(freshness_note)

    has_unprotected_sensitive = bool(
        (
            (classification_df["lgpd_classification"] == "sensitive_personal_data")
            & ~classification_df["recommended_action"].isin(["anonymize", "remove"])
        ).any()
    )

    gate_result = evaluate_publication_readiness(
        data_quality_score=_data_quality_score(quality_results),
        privacy_risk_score=int(risk_result["score"]),
        critical_rule_failures=critical_rule_failures,
        freshness_status=freshness_status,
        schema_contract_status=schema_contract_status,
        has_sensitive_data_without_protection=has_unprotected_sensitive,
    )
    return gate_result, fallback_notes


def _load_governance_history(path: Path = GOVERNANCE_HISTORY_PATH) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    history_df = pd.read_csv(path)
    if history_df.empty:
        return pd.DataFrame()
    if "execution_timestamp" in history_df.columns:
        history_df["execution_timestamp"] = pd.to_datetime(
            history_df["execution_timestamp"], errors="coerce", utc=True
        )
    elif "run_timestamp" in history_df.columns:
        history_df["execution_timestamp"] = pd.to_datetime(
            history_df["run_timestamp"], errors="coerce", utc=True
        )
    else:
        history_df["execution_timestamp"] = pd.NaT
    return history_df


def _render_governance_history_trends(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.markdown(
        "## Governance History" if is_en else "## Histórico de Governança"
    )
    history_df = _load_governance_history()

    if history_df.empty:
        st.info(
            "No governance snapshot has been persisted in this environment yet."
            if is_en
            else "Nenhum snapshot de governança foi persistido ainda neste ambiente."
        )
        return

    if len(history_df) < 2:
        st.info(
            "Only one governance run is available. Trend charts will become more informative with multiple runs."
            if is_en
            else "Apenas uma execução de governança disponível. Os gráficos de tendência ficam mais úteis com múltiplas execuções."
        )

    chart_df = history_df.sort_values("execution_timestamp").copy()

    # Normalize columns for backward compatibility with older history files.
    if (
        "privacy_risk_score" not in chart_df.columns
        and "privacy_score" in chart_df.columns
    ):
        chart_df["privacy_risk_score"] = chart_df["privacy_score"]
    if "row_count" not in chart_df.columns and "total_rows" in chart_df.columns:
        chart_df["row_count"] = chart_df["total_rows"]
    if (
        "failed_rules_count" not in chart_df.columns
        and "failed_checks_count" in chart_df.columns
    ):
        chart_df["failed_rules_count"] = chart_df["failed_checks_count"]
    for missing_col in [
        "warning_rules_count",
        "critical_rules_count",
        "publication_status",
        "data_quality_score",
    ]:
        if missing_col not in chart_df.columns:
            chart_df[missing_col] = 0 if "count" in missing_col else "unknown"

    col_left, col_right = st.columns(2)
    with col_left:
        dq_fig = px.line(
            chart_df,
            x="execution_timestamp",
            y="data_quality_score",
            markers=True,
            title="Data Quality Score Over Time"
            if is_en
            else "Score de Qualidade ao Longo do Tempo",
            labels={
                "execution_timestamp": "Execution timestamp"
                if is_en
                else "Data da execução",
                "data_quality_score": "Data quality score"
                if is_en
                else "Qualidade dos dados",
            },
        )
        dq_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(dq_fig, width="stretch")

    with col_right:
        pr_fig = px.line(
            chart_df,
            x="execution_timestamp",
            y="privacy_risk_score",
            markers=True,
            title="Privacy Risk Score Over Time"
            if is_en
            else "Score de Risco de Privacidade ao Longo do Tempo",
            labels={
                "execution_timestamp": "Execution timestamp"
                if is_en
                else "Data da execução",
                "privacy_risk_score": "Privacy risk score"
                if is_en
                else "Risco de privacidade",
            },
        )
        pr_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(pr_fig, width="stretch")

    col_left2, col_right2 = st.columns(2)
    with col_left2:
        status_counts = (
            chart_df["publication_status"]
            .astype(str)
            .value_counts()
            .rename_axis("publication_status")
            .reset_index(name="count")
        )
        status_counts_display = status_counts.copy()
        status_counts_display["publication_status"] = status_counts_display[
            "publication_status"
        ].map(
            lambda value: _presentation_label(
                value, _STATUS_LABELS_PT_BR, is_en=is_en
            )
        )
        status_fig = px.bar(
            status_counts_display,
            x="publication_status",
            y="count",
            color="publication_status",
            title="Publication Status Distribution"
            if is_en
            else "Distribuição de Status de Publicação",
            labels={
                "publication_status": "Publication status"
                if is_en
                else "Status de publicação",
                "count": "Count" if is_en else "Quantidade",
            },
        )
        status_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
        st.plotly_chart(status_fig, width="stretch")

    with col_right2:
        rules_cols = [
            "failed_rules_count",
            "warning_rules_count",
            "critical_rules_count",
        ]
        rules_df = chart_df[["execution_timestamp", *rules_cols]].melt(
            id_vars=["execution_timestamp"],
            value_vars=rules_cols,
            var_name="rule_type",
            value_name="count",
        )
        rules_fig = px.line(
            rules_df,
            x="execution_timestamp",
            y="count",
            color="rule_type",
            markers=True,
            title="Rules Severity Counts Over Time"
            if is_en
            else "Contagem de Regras por Severidade ao Longo do Tempo",
            labels={
                "execution_timestamp": "Execution timestamp"
                if is_en
                else "Data da execução",
                "count": "Count" if is_en else "Quantidade",
                "rule_type": "Rule type" if is_en else "Tipo de regra",
            },
        )
        rules_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(rules_fig, width="stretch")

    row_fig = px.line(
        chart_df,
        x="execution_timestamp",
        y="row_count",
        markers=True,
        title="Row Count Over Time" if is_en else "Volume de Linhas ao Longo do Tempo",
        labels={
            "execution_timestamp": "Execution timestamp"
            if is_en
            else "Data da execução",
            "row_count": "Rows" if is_en else "Linhas",
        },
    )
    row_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(row_fig, width="stretch")

    show_cols = [
        "run_id",
        "dataset_name",
        "execution_timestamp",
        "row_count",
        "data_quality_score",
        "privacy_risk_score",
        "publication_status",
        "failed_rules_count",
        "warning_rules_count",
        "critical_rules_count",
        "freshness_status",
    ]
    available_cols = [column for column in show_cols if column in chart_df.columns]
    technical_history = chart_df[available_cols].tail(30)
    presentation_history = technical_history.copy()
    if "publication_status" in presentation_history.columns:
        presentation_history["publication_status"] = presentation_history[
            "publication_status"
        ].map(
            lambda value: _presentation_label(
                value, _STATUS_LABELS_PT_BR, is_en=is_en
            )
        )
    presentation_history = presentation_history.rename(
        columns={
            "run_id": "Run ID" if is_en else "Execução",
            "dataset_name": "Dataset" if is_en else "Ativo",
            "execution_timestamp": "Execution timestamp"
            if is_en
            else "Data da execução",
            "row_count": "Rows" if is_en else "Linhas",
            "data_quality_score": "Data quality score"
            if is_en
            else "Qualidade dos dados",
            "privacy_risk_score": "Privacy risk score"
            if is_en
            else "Risco de privacidade",
            "publication_status": "Publication status"
            if is_en
            else "Status de publicação",
            "failed_rules_count": "Failed rules"
            if is_en
            else "Regras reprovadas",
            "warning_rules_count": "Warning rules"
            if is_en
            else "Regras em alerta",
            "critical_rules_count": "Critical rules"
            if is_en
            else "Regras críticas",
            "freshness_status": "Freshness" if is_en else "Atualização",
        }
    )
    st.markdown("### Monitoring history" if is_en else "### Histórico de monitoramento")
    st.dataframe(
        presentation_history,
        width="stretch",
        hide_index=True,
    )
    with st.expander(
        "Technical monitoring history"
        if is_en
        else "Histórico técnico de monitoramento",
        expanded=False,
    ):
        st.dataframe(technical_history, width="stretch")


def build_publication_decision_rationale(
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
    classification_df: pd.DataFrame,
) -> tuple[str, list[str], list[str], list[str]]:
    publication_status = _governance_status(
        risk_result["risk_level"], quality_results["failed_checks_count"]
    )
    personal_count = int(
        (classification_df["lgpd_classification"] == "personal_data").sum()
    )
    sensitive_count = int(
        (classification_df["lgpd_classification"] == "sensitive_personal_data").sum()
    )
    indirect_count = int(
        (classification_df["lgpd_classification"] == "indirect_identifier").sum()
    )

    reasons = [
        f"Privacy risk level: {risk_result['risk_level']} ({risk_result['score']}/100).",
        f"Failed quality checks: {quality_results['failed_checks_count']}.",
        f"Sensitive/personal/indirect columns: {sensitive_count}/{personal_count}/{indirect_count}.",
    ]
    actions = list(risk_result["recommendations"][:5])
    if quality_results["failed_checks_count"] > 0:
        actions.append("Remediate failed quality checks before executive publication.")

    evidence = [
        "LGPD classification inventory (column-level).",
        "Privacy risk score components and recommendation.",
        "Data quality checks table with PASS/FAIL status.",
        "Published-layer governance and privacy contract checks.",
    ]
    return publication_status, reasons, actions, evidence


def save_governance_snapshot(
    *,
    df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
    publication_status: str,
    history_path: Path | None = None,
) -> Path:
    if history_path is not None:
        return append_governance_history(
            total_rows=int(len(df)),
            total_columns=int(df.shape[1]),
            privacy_result=risk_result,
            quality_result=quality_results,
            publication_status=publication_status,
            history_path=history_path,
        )
    return append_governance_history(
        total_rows=int(len(df)),
        total_columns=int(df.shape[1]),
        privacy_result=risk_result,
        quality_result=quality_results,
        publication_status=publication_status,
    )


def render_governance_control_center(
    df: pd.DataFrame,
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_results: DataQualityResult,
    locale: Locale,
) -> None:
    is_en = locale == LOCALE_EN_US
    st.title("Governance Lab" if is_en else "Laboratório de Governança")
    st.subheader(
        (
            "Diagnostic environment combining a summarized view, canonical "
            "publication assessment, and optional snapshot persistence."
        )
        if is_en
        else (
            "Ambiente de diagnóstico que combina visão resumida, avaliação "
            "canônica de publicação e persistência opcional de snapshots."
        )
    )
    st.caption(
        (
            "This page does not replace the authoritative publication decision. "
            "The summarized diagnosis and the publication gate use different "
            "rules and may produce different results."
        )
        if is_en
        else (
            "Esta página não substitui a decisão autoritativa de publicação. O "
            "diagnóstico resumido e o publication gate usam regras diferentes e "
            "podem apresentar resultados distintos."
        )
    )
    st.markdown(
        "### How to interpret this page"
        if is_en
        else "### Como interpretar esta página"
    )
    st.write(
        (
            "Use the summarized diagnosis as a quick view of the context. The "
            "publication gate result is the canonical assessment available on "
            "this page. History is persisted only when the save action is run."
        )
        if is_en
        else (
            "Use o diagnóstico resumido como visão rápida do contexto. O "
            "resultado do publication gate representa a avaliação canônica "
            "disponível nesta página. O histórico só é persistido quando a ação "
            "de salvar é executada."
        )
    )
    privacy_columns = classification_df["lgpd_classification"]
    personal_count = int((privacy_columns == "personal_data").sum())
    sensitive_count = int((privacy_columns == "sensitive_personal_data").sum())
    indirect_count = int((privacy_columns == "indirect_identifier").sum())
    quality_score = _data_quality_score(quality_results)
    gate_result, gate_fallback_notes = _evaluate_publication_gate(
        classification_df=classification_df,
        risk_result=risk_result,
        quality_results=quality_results,
    )
    governance_status, rationale_reasons, rationale_actions, rationale_evidence = (
        build_publication_decision_rationale(
            risk_result,
            quality_results,
            classification_df,
        )
    )
    publication_status = governance_status

    st.markdown("## Summary" if is_en else "## Resumo")
    st.markdown("### Context" if is_en else "### Contexto")
    context_col1, context_col2, context_col3 = st.columns(3)
    context_col1.metric(
        "Personal Columns" if is_en else "Dados pessoais", personal_count
    )
    context_col2.metric(
        "Sensitive Columns" if is_en else "Dados sensíveis", sensitive_count
    )
    context_col3.metric(
        "Indirect Identifier Columns"
        if is_en
        else "Identificadores indiretos",
        indirect_count,
    )

    st.markdown("### Risk" if is_en else "### Risco")
    risk_col = st.columns(1)[0]
    risk_col.metric(
        "Privacy Risk Score" if is_en else "Risco de privacidade",
        f"{risk_result['score']} / 100",
    )

    st.markdown("### Quality" if is_en else "### Qualidade")
    quality_col1, quality_col2 = st.columns(2)
    quality_col1.metric(
        "Data Quality Score" if is_en else "Qualidade dos dados",
        f"{quality_score} / 100",
    )
    quality_col2.metric(
        "Failed Checks" if is_en else "Checks reprovados",
        quality_results["failed_checks_count"],
    )

    st.markdown("### Decision" if is_en else "### Decisão")
    decision_col1, decision_col2 = st.columns(2)
    decision_col1.metric(
        "Governance Status" if is_en else "Diagnóstico resumido",
        _presentation_label(
            governance_status, _STATUS_LABELS_PT_BR, is_en=is_en
        ),
    )
    decision_col2.metric(
        "Publication Readiness" if is_en else "Resultado do publication gate",
        _presentation_label(
            gate_result.decision, _STATUS_LABELS_PT_BR, is_en=is_en
        ),
    )

    st.markdown("## Diagnosis" if is_en else "## Diagnóstico")
    st.caption(
        "The summarized diagnosis and the publication gate are different mechanisms."
        if is_en
        else "O diagnóstico resumido e o publication gate são mecanismos diferentes."
    )
    displayed_governance_status = _presentation_label(
        governance_status, _STATUS_LABELS_PT_BR, is_en=is_en
    )
    if publication_status == "Approved":
        st.success(
            f"{'Summarized diagnosis' if is_en else 'Diagnóstico resumido'}: "
            f"{displayed_governance_status}",
            icon="✅",
        )
    elif publication_status == "Needs Review":
        st.warning(
            f"{'Summarized diagnosis' if is_en else 'Diagnóstico resumido'}: "
            f"{displayed_governance_status}",
            icon="⚠️",
        )
    else:
        st.error(
            f"{'Summarized diagnosis' if is_en else 'Diagnóstico resumido'}: "
            f"{displayed_governance_status}",
            icon="⛔",
        )

    charts_col1, charts_col2 = st.columns(2)
    with charts_col1:
        st.markdown(
            "**LGPD classification distribution**"
            if is_en
            else "**Distribuição das classificações LGPD**"
        )
        class_counts = (
            classification_df["lgpd_classification"]
            .value_counts()
            .rename_axis("classification")
            .reset_index(name="count")
        )
        class_counts_display = class_counts.copy()
        class_counts_display["classification"] = class_counts_display[
            "classification"
        ].map(
            lambda value: _presentation_label(
                value, _CLASSIFICATION_LABELS_PT_BR, is_en=is_en
            )
        )
        fig_class = px.bar(
            class_counts_display,
            x="classification",
            y="count",
            color="classification",
            title="LGPD classification distribution"
            if is_en
            else "Distribuição das classificações LGPD",
            labels={
                "classification": "LGPD classification"
                if is_en
                else "Classificação LGPD",
                "count": "Count" if is_en else "Quantidade",
            },
        )
        fig_class.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_class, width="stretch")

    with charts_col2:
        st.markdown(
            "**Data quality check distribution**"
            if is_en
            else "**Distribuição dos checks de qualidade**"
        )
        checks_df = pd.DataFrame(quality_results["checks"])
        if checks_df.empty:
            st.info(
                "No quality checks available."
                if is_en
                else "Nenhum check de qualidade disponível."
            )
        else:
            status_counts = (
                checks_df["status"]
                .value_counts()
                .rename_axis("status")
                .reset_index(name="count")
            )
            status_counts_display = status_counts.copy()
            status_counts_display["status"] = status_counts_display["status"].map(
                lambda value: _presentation_label(
                    value, _CHECK_STATUS_LABELS_PT_BR, is_en=is_en
                )
            )
            fig_checks = px.bar(
                status_counts_display,
                x="status",
                y="count",
                color="status",
                title="Data quality check distribution"
                if is_en
                else "Distribuição dos checks de qualidade",
                labels={
                    "status": "Status",
                    "count": "Count" if is_en else "Quantidade",
                },
            )
            fig_checks.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_checks, width="stretch")

    st.markdown(
        "### Columns with highest review priority"
        if is_en
        else "### Colunas com maior prioridade de revisão"
    )
    top_risky_columns = classification_df[
        classification_df["lgpd_classification"].isin(
            ["sensitive_personal_data", "personal_data", "indirect_identifier"]
        )
    ].copy()
    risk_rank = {
        "sensitive_personal_data": 3,
        "personal_data": 2,
        "indirect_identifier": 1,
    }
    top_risky_columns["risk_rank"] = (
        top_risky_columns["lgpd_classification"].map(risk_rank).fillna(0)
    )
    top_risky_columns = top_risky_columns.sort_values(
        by=["risk_rank", "risk_level", "column_name"], ascending=[False, False, True]
    )
    technical_top_risky_columns = top_risky_columns[
        [
            "column_name",
            "lgpd_classification",
            "risk_level",
            "recommended_action",
            "reason",
        ]
    ].head(10)
    presentation_top_risky_columns = technical_top_risky_columns.copy()
    presentation_top_risky_columns["lgpd_classification"] = (
        presentation_top_risky_columns["lgpd_classification"].map(
            lambda value: _presentation_label(
                value, _CLASSIFICATION_LABELS_PT_BR, is_en=is_en
            )
        )
    )
    presentation_top_risky_columns["risk_level"] = presentation_top_risky_columns[
        "risk_level"
    ].map(
        lambda value: _presentation_label(
            value, _SEVERITY_LABELS_PT_BR, is_en=is_en
        )
    )
    presentation_top_risky_columns["recommended_action"] = (
        presentation_top_risky_columns["recommended_action"].map(
            lambda value: _presentation_label(
                value, _ACTION_LABELS_PT_BR, is_en=is_en
            )
        )
    )
    presentation_top_risky_columns = presentation_top_risky_columns.rename(
        columns={
            "column_name": "Column" if is_en else "Coluna",
            "lgpd_classification": "LGPD classification"
            if is_en
            else "Classificação LGPD",
            "risk_level": "Risk level" if is_en else "Nível de risco",
            "recommended_action": "Recommended action"
            if is_en
            else "Ação recomendada",
            "reason": "Reason" if is_en else "Motivo",
        }
    )
    st.dataframe(
        presentation_top_risky_columns,
        width="stretch",
        hide_index=True,
    )

    with st.expander(
        "Risk Details" if is_en else "Detalhes dos Riscos", expanded=False
    ):
        st.markdown("**Top Risks**" if is_en else "**Principais Riscos**")
        failed_checks = [
            check for check in quality_results["checks"] if check["status"] == "FAIL"
        ]
        if not failed_checks and risk_result["risk_level"] == "low":
            st.write(
                "- No critical governance risks detected."
                if is_en
                else "- Nenhum risco crítico de governança detectado."
            )
        else:
            for check in failed_checks[:5]:
                st.write(f"- {check['check_name']}: {check['recommendation']}")
            if risk_result["risk_level"] in {"medium", "high"}:
                st.write(
                    f"- Privacy risk level is {risk_result['risk_level']} (score {risk_result['score']})."
                )

        st.markdown("**Recommended Actions**" if is_en else "**Ações Recomendadas**")
        for recommendation in risk_result["recommendations"][:5]:
            st.write(f"- {recommendation}")

    st.markdown("### Technical summary" if is_en else "### Leitura técnica")
    if is_en:
        st.write(
            f"This dataset has {len(df)} rows and {df.shape[1]} columns. Governance status is {governance_status}. "
            f"Privacy risk is {risk_result['risk_level']} ({risk_result['score']}/100) and data quality score is {quality_score}/100. "
            f"Publication decision: {publication_status}."
        )
    else:
        st.write(
            f"Este dataset possui {len(df)} linhas e {df.shape[1]} colunas. O status de governança é {governance_status}. "
            f"O risco de privacidade é {risk_result['risk_level']} ({risk_result['score']}/100) e o score de qualidade é {quality_score}/100. "
            f"Decisão de publicação: {publication_status}."
        )

    with st.expander(
        "Decision Rationale" if is_en else "Racional da Decisão", expanded=False
    ):
        for line in rationale_reasons:
            st.write(f"- {line}")

    st.markdown("## Publication Gate")
    st.write(
        f"**{'Decision' if is_en else 'Decisão'}:** "
        f"{_presentation_label(gate_result.decision, _STATUS_LABELS_PT_BR, is_en=is_en)}"
    )
    st.write(
        f"**{'Severity' if is_en else 'Severidade'}:** "
        f"{_presentation_label(gate_result.severity, _SEVERITY_LABELS_PT_BR, is_en=is_en)}"
    )
    if governance_status != gate_result.decision:
        st.info(
            "The results differ because they use distinct rules and criteria."
            if is_en
            else "Os resultados diferem porque usam regras e critérios distintos."
        )

    st.markdown("**Gate Reasons**" if is_en else "**Motivos do Gate**")
    for reason in gate_result.reasons:
        st.write(f"- {reason}")

    st.markdown(
        "**Gate Required Actions**" if is_en else "**Ações Obrigatórias do Gate**"
    )
    for action in gate_result.required_actions:
        st.write(f"- {action}")

    st.markdown(
        "### Publication gate criteria"
        if is_en
        else "### Critérios do publication gate"
    )
    criteria = (
        [
            "Data quality below 80 requires review.",
            "Privacy risk at or above 60 requires review.",
            "Privacy risk at or above 80 raises severity to High.",
            "A critical failure blocks publication.",
            "Sensitive data without anonymize/remove blocks publication.",
            "Schema contract status equal to failed blocks publication.",
            "Freshness warning or stale requires review.",
            "Freshness stale raises severity to High.",
        ]
        if is_en
        else [
            "Qualidade abaixo de 80 requer revisão.",
            "Risco de privacidade a partir de 60 requer revisão.",
            "Risco de privacidade a partir de 80 eleva a severidade para Alta.",
            "Falha crítica bloqueia a publicação.",
            "Dado sensível sem anonymize/remove bloqueia a publicação.",
            "Contrato de schema com status failed bloqueia a publicação.",
            "Freshness warning ou stale requer revisão.",
            "Freshness stale eleva a severidade para Alta.",
        ]
    )
    for criterion in criteria:
        st.write(f"- {criterion}")

    st.markdown(
        "### Assumptions and fallbacks" if is_en else "### Suposições e fallbacks"
    )
    st.warning(
        (
            "Under the existing rules, the schema contract may be assumed as "
            "passed and freshness as fresh when expected artifacts are missing, "
            "invalid, empty, or cannot be read. A fallback is not observed evidence."
        )
        if is_en
        else (
            "Nas regras atuais, o contrato pode ser assumido como passed e a "
            "freshness como fresh quando os artefatos esperados estão ausentes, "
            "inválidos, vazios ou não podem ser lidos. Um fallback não representa "
            "evidência observada."
        )
    )
    if gate_fallback_notes:
        for note in gate_fallback_notes:
            st.write(f"- {note}")
    else:
        st.caption(
            "No fallback assumption was applied to this evaluation."
            if is_en
            else "Nenhuma suposição de fallback foi aplicada nesta avaliação."
        )

    st.markdown(
        "**Executive Recommendation**" if is_en else "**Recomendação Executiva Final**"
    )
    recommendation_text = (
        "Proceed to publication with routine monitoring."
        if publication_status == "Approved"
        else (
            "Hold publication for control review and remediation actions."
            if publication_status == "Needs Review"
            else "Block publication until privacy controls and quality failures are remediated."
        )
    )
    if not is_en:
        recommendation_text = (
            "Prosseguir com a publicação e monitoramento de rotina."
            if publication_status == "Approved"
            else (
                "Segurar a publicação para revisão de controles e ações de remediação."
                if publication_status == "Needs Review"
                else "Bloquear a publicação até remediar controles de privacidade e falhas de qualidade."
            )
        )
    if publication_status == "Approved":
        st.success(recommendation_text)
    elif publication_status == "Needs Review":
        st.warning(recommendation_text)
    else:
        st.error(recommendation_text)

    st.markdown(
        "### ⚠️ Persistent action" if is_en else "### ⚠️ Ação com persistência"
    )
    st.warning(
        (
            "The button below writes a snapshot to governance history and updates "
            "the persisted decision artifact. It is not only a visual simulation."
        )
        if is_en
        else (
            "O botão abaixo grava um snapshot no histórico de governança e "
            "atualiza o artefato de decisão persistida. Ele não é apenas uma "
            "simulação visual."
        )
    )
    button_label = (
        "Save snapshot and update persisted decision"
        if is_en
        else "Salvar snapshot e atualizar decisão persistida"
    )
    saved_path: Path | None = None
    if st.button(button_label, type="primary"):
        saved_path = save_governance_snapshot(
            df=df,
            risk_result=risk_result,
            quality_results=quality_results,
            publication_status=publication_status,
        )
        st.success(
            "Governance snapshot and persisted decision updated."
            if is_en
            else "Snapshot de governança e decisão persistida atualizados."
        )

    st.divider()
    _render_governance_history_trends(locale)

    with st.expander(
        "Technical lab details"
        if is_en
        else "Detalhes técnicos do laboratório",
        expanded=False,
    ):
        st.caption(GOVERNANCE_LAB_NOTICE)
        st.write(f"governance_status: `{governance_status}`")
        st.write(f"publication_status: `{publication_status}`")
        st.write(f"gate.decision: `{gate_result.decision}`")
        st.write(f"gate.severity: `{gate_result.severity}`")
        st.caption(f"governance_history_path: `{GOVERNANCE_HISTORY_PATH}`")
        st.caption(
            f"schema_contract_results_path: `{SCHEMA_CONTRACT_RESULTS_PATH}`"
        )
        st.caption(
            f"published_monitoring_results_path: `{PUBLISHED_MONITORING_RESULTS_PATH}`"
        )
        if saved_path is not None:
            st.caption(f"saved_history_path: `{saved_path.resolve()}`")

        st.markdown("**Top Risky Columns — technical values**")
        st.dataframe(technical_top_risky_columns, width="stretch")

        st.markdown("**Quality checks — technical values**")
        if checks_df.empty:
            st.info("No quality checks available.")
        else:
            st.dataframe(checks_df, width="stretch")

        st.markdown("**Decision rationale — technical values**")
        for reason in rationale_reasons:
            st.write(f"- {reason}")
        for action in rationale_actions:
            st.write(f"- {action}")
        for item in rationale_evidence:
            st.write(f"- {item}")

        st.markdown("**Gate assumptions / fallbacks — technical values**")
        for note in gate_fallback_notes:
            st.write(f"- {note}")
