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
PUBLISHED_MONITORING_RESULTS_PATH = (
    PUBLISHED_MONITORING_DIR / "published_layer_monitoring.csv"
)


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
        return "passed", "Schema contract results could not be parsed; assumed 'passed'."
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
        return "fresh", "Published monitoring file could not be parsed; assumed 'fresh'."
    if checks_df.empty or "check_name" not in checks_df.columns:
        return "fresh", "Published monitoring checks are empty/invalid; assumed 'fresh'."

    freshness_rows = checks_df[
        checks_df["check_name"].astype(str) == "published_file_freshness_hours"
    ]
    if freshness_rows.empty:
        return "fresh", "Freshness check not found in monitoring results; assumed 'fresh'."

    freshness_row = freshness_rows.iloc[-1]
    status = str(freshness_row.get("status", "")).upper()
    if status == "PASS":
        return "fresh", None

    metric_value = pd.to_numeric(freshness_row.get("metric_value"), errors="coerce")
    threshold = pd.to_numeric(freshness_row.get("threshold"), errors="coerce")
    if pd.notna(metric_value) and pd.notna(threshold) and float(metric_value) <= float(
        threshold
    ) * 1.5:
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
        "## Governance Monitoring Trends"
        if is_en
        else "## Tendências de Monitoramento de Governança"
    )
    history_df = _load_governance_history()

    if history_df.empty:
        st.info(
            "No governance history runs found yet. Trends will appear after at least one snapshot is saved."
            if is_en
            else "Nenhuma execução histórica encontrada. As tendências aparecerão após salvar ao menos um snapshot."
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
        status_fig = px.bar(
            status_counts,
            x="publication_status",
            y="count",
            color="publication_status",
            title="Publication Status Distribution"
            if is_en
            else "Distribuição de Status de Publicação",
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
        )
        rules_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(rules_fig, width="stretch")

    row_fig = px.line(
        chart_df,
        x="execution_timestamp",
        y="row_count",
        markers=True,
        title="Row Count Over Time" if is_en else "Volume de Linhas ao Longo do Tempo",
    )
    row_fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(row_fig, width="stretch")

    with st.expander(
        "Monitoring History Table" if is_en else "Tabela de Histórico de Monitoramento",
        expanded=False,
    ):
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
        st.dataframe(chart_df[available_cols].tail(30), width="stretch")


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
    st.subheader(
        "Governance Control Center" if is_en else "Central de Controles de Governança"
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

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Governance Status" if is_en else "Status de Governança", governance_status
    )
    col2.metric(
        "Privacy Risk Score" if is_en else "Score de Risco de Privacidade",
        f"{risk_result['score']} / 100",
    )
    col3.metric(
        "Data Quality Score" if is_en else "Score de Qualidade",
        f"{quality_score} / 100",
    )
    col4.metric(
        "Failed Checks" if is_en else "Checks Reprovados",
        quality_results["failed_checks_count"],
    )

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Personal Columns" if is_en else "Colunas Pessoais", personal_count)
    col6.metric("Sensitive Columns" if is_en else "Colunas Sensíveis", sensitive_count)
    col7.metric(
        "Indirect Identifier Columns" if is_en else "Identificadores Indiretos",
        indirect_count,
    )
    col8.metric(
        "Publication Readiness" if is_en else "Prontidão para Publicação",
        publication_status,
    )

    if publication_status == "Approved":
        st.success(
            f"{'Publication Status' if is_en else 'Status de Publicação'}: {publication_status}",
            icon="✅",
        )
    elif publication_status == "Needs Review":
        st.warning(
            f"{'Publication Status' if is_en else 'Status de Publicação'}: {publication_status}",
            icon="⚠️",
        )
    else:
        st.error(
            f"{'Publication Status' if is_en else 'Status de Publicação'}: {publication_status}",
            icon="⛔",
        )

    charts_col1, charts_col2 = st.columns(2)
    with charts_col1:
        st.markdown(
            "**LGPD Classification Distribution**"
            if is_en
            else "**Distribuição de Classificação LGPD**"
        )
        class_counts = (
            classification_df["lgpd_classification"]
            .value_counts()
            .rename_axis("classification")
            .reset_index(name="count")
        )
        fig_class = px.bar(
            class_counts,
            x="classification",
            y="count",
            color="classification",
        )
        fig_class.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_class, width="stretch")

    with charts_col2:
        st.markdown(
            "**Data Quality Checks (PASS vs FAIL)**"
            if is_en
            else "**Checks de Qualidade (PASS vs FAIL)**"
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
            fig_checks = px.bar(status_counts, x="status", y="count", color="status")
            fig_checks.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_checks, width="stretch")

    st.markdown("**Top Risky Columns**" if is_en else "**Colunas Mais Arriscadas**")
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
    st.dataframe(
        top_risky_columns[
            [
                "column_name",
                "lgpd_classification",
                "risk_level",
                "recommended_action",
                "reason",
            ]
        ].head(10),
        width="stretch",
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

    st.markdown("**Executive Summary**" if is_en else "**Resumo Executivo**")
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

    st.markdown("## Publication Decision" if is_en else "## Decisão de Publicação")
    st.markdown("**Decision**" if is_en else "**Decisão**")
    st.write(publication_status)
    st.markdown("**Main Reasons**" if is_en else "**Principais Motivos**")
    for reason in rationale_reasons:
        st.write(f"- {reason}")
    st.markdown("**Recommended Actions**" if is_en else "**Ações Recomendadas**")
    for action in rationale_actions:
        st.write(f"- {action}")
    st.markdown("**Evidence Generated**" if is_en else "**Evidências Geradas**")
    for item in rationale_evidence:
        st.write(f"- {item}")

    st.markdown(
        "### Publication Gate Output" if is_en else "### Saída do Publication Gate"
    )
    gate_col1, gate_col2 = st.columns(2)
    gate_col1.metric(
        "Gate Decision" if is_en else "Decisão do Gate", gate_result.decision
    )
    gate_col2.metric(
        "Gate Severity" if is_en else "Severidade do Gate", gate_result.severity
    )

    st.markdown("**Gate Reasons**" if is_en else "**Motivos do Gate**")
    for reason in gate_result.reasons:
        st.write(f"- {reason}")

    st.markdown(
        "**Gate Required Actions**" if is_en else "**Ações Obrigatórias do Gate**"
    )
    for action in gate_result.required_actions:
        st.write(f"- {action}")

    with st.expander(
        "Gate Assumptions / Fallbacks" if is_en else "Premissas / Fallbacks do Gate",
        expanded=False,
    ):
        for note in gate_fallback_notes:
            st.write(f"- {note}")

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

    button_label = (
        "Save Governance Snapshot" if is_en else "Salvar Snapshot de Governança"
    )
    if st.button(button_label, type="primary"):
        saved_path = save_governance_snapshot(
            df=df,
            risk_result=risk_result,
            quality_results=quality_results,
            publication_status=publication_status,
        )
        if is_en:
            st.success(f"Governance snapshot saved to: {saved_path.resolve()}")
        else:
            st.success(f"Snapshot de governança salvo em: {saved_path.resolve()}")

    st.divider()
    with st.expander(
        "📈 Tendências Históricas de Governança"
        if not is_en
        else "📈 Governance Historical Trends",
        expanded=False,
    ):
        _render_governance_history_trends(locale)
