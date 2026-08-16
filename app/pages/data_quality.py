from __future__ import annotations

import pandas as pd
import streamlit as st

from app.i18n import Locale
from src.governance_types import DataQualityResult

_STATUS_LABELS = {
    "PASS": "APROVADO",
    "WARN": "ALERTA",
    "FAIL": "FALHA",
}

_SEVERITY_LABELS = {
    "high": "ALTA",
    "medium": "MÉDIA",
    "low": "BAIXA",
}

_CHECK_LABELS = {
    "order_id_unique": "Unicidade do pedido",
    "revenue_accepted_range": "Faixa válida de receita",
    "revenue_no_negative": "Receita não negativa",
    "order_status_allowed_values": "Status de pedido permitido",
}

_COLUMN_LABELS = {
    "order_id": "ID do pedido",
    "revenue": "Receita",
    "order_status": "Status do pedido",
    "seller_state": "Estado do seller",
    "product_category": "Categoria do produto",
    "delivery_time_days": "Tempo de entrega (dias)",
    "estimated_days": "Prazo estimado (dias)",
    "customer_unique_id": "Cliente",
}

_CHART_COLUMN_LABELS = {
    "carrier_delivery_time_days": "Entrega transportadora",
    "estimated_delivery_days": "Prazo estimado",
    "delivery_time_days": "Tempo de entrega",
    "product_category": "Categoria produto",
    "seller_state": "Estado seller",
    "customer_unique_id": "Cliente",
    "order_status": "Status pedido",
    "revenue": "Receita",
}

_RECOMMENDATION_LABELS = {
    "Ensure order identifiers are unique in the analytical grain.": (
        "Garantir unicidade dos identificadores de pedido na granularidade "
        "analítica."
    ),
    "Review outlier revenue records and business rule boundaries.": (
        "Revisar valores atípicos de receita e os limites definidos pelas "
        "regras de negócio."
    ),
    "Negative revenue should be justified or corrected.": (
        "Valores negativos de receita devem ser justificados ou corrigidos."
    ),
    "Standardize order status values according to contract.": (
        "Padronizar os valores de status do pedido conforme o contrato de dados."
    ),
}

_EXECUTIVE_COLUMN_LABELS = {
    "check_name": "Validação",
    "status": "Status",
    "severity": "Severidade",
    "affected_columns": "Colunas afetadas",
    "affected_rows": "Linhas afetadas",
    "recommendation": "Recomendação",
    "rule_source": "Origem da regra",
}


def _humanize_identifier(value: object) -> str:
    return str(value).replace("_", " ").strip().capitalize()


def _display_check_name(value: object) -> str:
    technical_name = str(value)
    return _CHECK_LABELS.get(technical_name, _humanize_identifier(technical_name))


def _display_column_name(value: object) -> str:
    technical_name = str(value)
    return _COLUMN_LABELS.get(technical_name, _humanize_identifier(technical_name))


def _display_chart_column_name(value: object) -> str:
    technical_name = str(value)
    fallback = _humanize_identifier(technical_name)
    if len(fallback) > 24:
        fallback = f"{fallback[:23].rstrip()}…"
    return _CHART_COLUMN_LABELS.get(technical_name, fallback)


def _display_affected_columns(value: object) -> object:
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_display_column_name(column) for column in value)
    if isinstance(value, str):
        return ", ".join(
            _display_column_name(column.strip()) for column in value.split(",")
        )
    return value


def _build_executive_table(quality_table: pd.DataFrame) -> pd.DataFrame:
    available_columns = [
        column for column in _EXECUTIVE_COLUMN_LABELS if column in quality_table
    ]
    display_table = quality_table.loc[:, available_columns].copy()
    if "check_name" in display_table:
        display_table["check_name"] = display_table["check_name"].map(
            _display_check_name
        )
    if "status" in display_table:
        display_table["status"] = display_table["status"].map(
            lambda value: _STATUS_LABELS.get(str(value).upper(), str(value))
        )
    if "severity" in display_table:
        display_table["severity"] = display_table["severity"].map(
            lambda value: _SEVERITY_LABELS.get(str(value).lower(), str(value))
        )
    if "affected_columns" in display_table:
        display_table["affected_columns"] = display_table["affected_columns"].map(
            _display_affected_columns
        )
    if "recommendation" in display_table:
        display_table["recommendation"] = display_table["recommendation"].map(
            lambda value: _RECOMMENDATION_LABELS.get(str(value), str(value))
        )
    return display_table.rename(columns=_EXECUTIVE_COLUMN_LABELS)


def _format_integer(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def render_data_quality(
    quality_results: DataQualityResult, quality_table: pd.DataFrame, locale: Locale
) -> None:
    del locale
    st.title("Qualidade dos Dados")
    st.markdown(
        "Visão executiva dos controles de integridade, consistência e regras "
        "de qualidade aplicados antes da publicação analítica."
    )
    st.caption(
        "Os indicadores apresentados refletem validações técnicas do dataset "
        "demonstrativo utilizado no projeto de portfólio."
    )
    st.markdown("### Como interpretar esta página")
    st.write(
        "A página demonstra como a plataforma identifica falhas de integridade, "
        "inconsistências e violações de regras antes que os dados sejam "
        "disponibilizados para consumo analítico."
    )

    failed_checks_count = int(quality_results["failed_checks_count"])
    quality_score = max(0, 100 - failed_checks_count * 10)

    total_checks = len(quality_table)
    pass_count = (
        int((quality_table["status"] == "PASS").sum())
        if "status" in quality_table.columns
        else 0
    )
    warn_count = (
        int((quality_table["status"] == "WARN").sum())
        if "status" in quality_table.columns
        else 0
    )
    fail_count = (
        int((quality_table["status"] == "FAIL").sum())
        if "status" in quality_table.columns
        else 0
    )

    high_fail_count = 0
    medium_fail_count = 0
    if {"status", "severity"}.issubset(quality_table.columns):
        failed_df = quality_table[quality_table["status"] == "FAIL"]
        high_fail_count = int((failed_df["severity"] == "high").sum())
        medium_fail_count = int((failed_df["severity"] == "medium").sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de validações", _format_integer(total_checks))
    with col2:
        st.metric("Aprovadas", _format_integer(pass_count))
    with col3:
        st.metric("Alertas", _format_integer(warn_count))
    with col4:
        st.metric("Falhas", _format_integer(fail_count))

    col5, col6, col7 = st.columns(3)
    with col5:
        st.metric("Total de linhas", _format_integer(quality_results["total_rows"]))
    with col6:
        st.metric("Total de colunas", _format_integer(quality_results["total_columns"]))
    with col7:
        st.metric("Score de qualidade", f"{quality_score} / 100")
    st.caption(
        "O score resume o resultado das validações técnicas do cenário "
        "demonstrativo."
    )

    st.markdown("### Leitura executiva")
    st.markdown(
        f"- **{pass_count}** validações foram aprovadas, **{warn_count}** "
        f"geraram alerta e **{fail_count}** apresentaram falha.\n"
        f"- O score de qualidade registrado para o cenário é "
        f"**{quality_score} / 100**."
    )

    null_profile = pd.DataFrame(
        list(quality_results["null_pct_by_column"].items()),
        columns=["column_name", "null_pct"],
    ).sort_values("null_pct", ascending=False)
    if not null_profile.empty:
        display_null_profile = null_profile.head(20).assign(
            column_label=null_profile["column_name"].map(
                _display_chart_column_name
            )
        )
        st.markdown("### Percentual de valores nulos por campo")
        st.bar_chart(
            display_null_profile,
            x="column_label",
            y="null_pct",
            x_label="Percentual de valores nulos",
            y_label="Campo",
            horizontal=True,
            sort=False,
        )

    status_df = quality_table["status"].value_counts().reset_index()
    status_df.columns = ["status", "count"]
    display_status = status_df.assign(
        status_label=status_df["status"].map(
            lambda value: _STATUS_LABELS.get(str(value).upper(), str(value))
        )
    )
    st.bar_chart(display_status.set_index("status_label")["count"])

    st.markdown("### Validações críticas com falha")
    if {"status", "severity"}.issubset(quality_table.columns):
        critical_failed = quality_table[
            (quality_table["status"] == "FAIL")
            & (quality_table["severity"].isin(["high", "medium"]))
        ]
        if critical_failed.empty:
            st.success("Nenhuma falha crítica de severidade alta ou média encontrada.")
        else:
            st.dataframe(
                _build_executive_table(critical_failed),
                width="stretch",
                hide_index=True,
            )

    st.markdown("### Resultado da avaliação")
    if high_fail_count > 0:
        st.error("Bloqueado")
        st.caption(
            "O cenário demonstrativo contém validações com falha e, por isso, "
            "a publicação é bloqueada pelas regras de qualidade."
        )
    elif medium_fail_count > 0 or fail_count > 0:
        st.warning("Requer revisão")
        st.caption(
            "O cenário demonstrativo requer revisão das falhas identificadas "
            "antes da publicação analítica."
        )
    else:
        st.success("Confiável")

    with st.expander("Detalhes técnicos das validações", expanded=False):
        st.metric("PASS / WARN / FAIL", f"{pass_count} / {warn_count} / {fail_count}")
        st.metric(
            "Severity raw (high / medium)",
            f"{high_fail_count} / {medium_fail_count}",
        )
        st.dataframe(quality_table, width="stretch", hide_index=True)
