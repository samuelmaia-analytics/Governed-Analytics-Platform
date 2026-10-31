from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as st

from app.components.cards import render_metric_cards
from src.config import PUBLISHED_MONITORING_DIR, QUALITY_DIR

PUBLICATION_DECISION_PATH = PUBLISHED_MONITORING_DIR / "publication_decision.json"
SHADOW_TELEMETRY_PATH = (
    PUBLISHED_MONITORING_DIR / "publication_shadow_comparisons.jsonl"
)
DUAL_PRIVACY_TELEMETRY_PATH = (
    PUBLISHED_MONITORING_DIR / "dual_privacy_shadow_comparisons.jsonl"
)
CONTENT_PROVENANCE_PATH = (
    PUBLISHED_MONITORING_DIR / "dataset_content_provenance.jsonl"
)
PRIVACY_RESULTS_PATH = QUALITY_DIR / "privacy_governance_results.csv"
SCHEMA_RESULTS_PATH = QUALITY_DIR / "schema_contract_results.csv"
BUSINESS_RESULTS_PATH = QUALITY_DIR / "business_rule_results.csv"
QUALITY_RESULTS_PATH = QUALITY_DIR / "fact_orders_enriched_quality_checks.csv"
MONITORING_RESULTS_PATH = PUBLISHED_MONITORING_DIR / "published_layer_monitoring.csv"

DIAGNOSTIC_NOTICE = (
    "As avaliações shadow e residual são diagnósticas e dependem de execução "
    "controlada. Elas não alteram a decisão histórica de publicação."
)
EVIDENCE_NOT_PERSISTED = "Evidência não persistida neste ambiente"
VALIDATIONS_DEMONSTRATED = "Validações demonstradas"


@dataclass(frozen=True)
class CheckSummary:
    passed: int
    warning: int
    failed: int
    total: int

    @property
    def display(self) -> str:
        parts = [f"{self.passed}/{self.total} PASS"]
        if self.warning:
            parts.append(f"{self.warning} WARN")
        if self.failed:
            parts.append(f"{self.failed} FAIL")
        return " · ".join(parts)


@dataclass(frozen=True)
class PublicationGovernanceSnapshot:
    run_id: str
    historical_decision: str
    shadow_decision: str
    shadow_severity: str
    residual_decision: str
    residual_severity: str
    inherent_score: int | None
    residual_score: int | None
    divergence_type: str
    sensitive_data_protected: bool | None
    privacy: CheckSummary
    schema: CheckSummary
    business: CheckSummary
    quality: CheckSummary
    monitoring: CheckSummary
    execution_provenance: str
    content_provenance: str
    source_fingerprint: str
    published_fingerprint: str


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    return value if isinstance(value, dict) else {}


def _load_last_jsonl(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    last_record: dict[str, Any] = {}
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            value = json.loads(line)
            if isinstance(value, dict):
                last_record = value
    return last_record


def _load_check_summary(path: Path) -> CheckSummary:
    if not path.exists():
        return CheckSummary(0, 0, 0, 0)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        statuses = [
            str(row.get("status", "")).strip().upper()
            for row in csv.DictReader(stream)
        ]
    return CheckSummary(
        passed=statuses.count("PASS"),
        warning=statuses.count("WARN"),
        failed=sum(status in {"FAIL", "FAILED", "ERROR"} for status in statuses),
        total=len(statuses),
    )


def _text(record: dict[str, Any], field: str) -> str:
    value = record.get(field)
    return str(value) if value is not None else "Unavailable"


def _score(record: dict[str, Any], field: str) -> int | None:
    value = record.get(field)
    return int(value) if isinstance(value, int | float) else None


def load_publication_governance_snapshot(
    *,
    decision_path: Path = PUBLICATION_DECISION_PATH,
    shadow_path: Path = SHADOW_TELEMETRY_PATH,
    dual_path: Path = DUAL_PRIVACY_TELEMETRY_PATH,
    content_path: Path = CONTENT_PROVENANCE_PATH,
    privacy_path: Path = PRIVACY_RESULTS_PATH,
    schema_path: Path = SCHEMA_RESULTS_PATH,
    business_path: Path = BUSINESS_RESULTS_PATH,
    quality_path: Path = QUALITY_RESULTS_PATH,
    monitoring_path: Path = MONITORING_RESULTS_PATH,
) -> PublicationGovernanceSnapshot:
    """Build a read-only portfolio view from already persisted evidence."""
    decision = _load_json(decision_path)
    shadow = _load_last_jsonl(shadow_path)
    dual = _load_last_jsonl(dual_path)
    content = _load_last_jsonl(content_path)
    privacy = _load_check_summary(privacy_path)

    telemetry_run_ids = {
        str(record["run_id"])
        for record in (shadow, dual)
        if record.get("run_id") is not None
    }
    run_id = _text(dual or shadow or content, "run_id")
    execution_valid = (
        len(telemetry_run_ids) == 1
        and bool(shadow.get("provenance_valid"))
        and bool(dual.get("evaluated"))
    )
    content_current = content.get("run_id") == run_id

    # This is a presentation summary of persisted controls, not a replacement for
    # the same-run protection evaluator used by the pipeline.
    protected = privacy.total > 0 and privacy.passed == privacy.total

    return PublicationGovernanceSnapshot(
        run_id=run_id,
        historical_decision=_text(decision, "status"),
        shadow_decision=_text(shadow, "canonical_decision"),
        shadow_severity=_text(shadow, "canonical_severity"),
        residual_decision=_text(dual, "residual_decision"),
        residual_severity=_text(dual, "residual_severity"),
        inherent_score=_score(dual, "inherent_score"),
        residual_score=_score(dual, "residual_score"),
        divergence_type=_text(dual, "divergence_type"),
        sensitive_data_protected=protected if privacy.total else None,
        privacy=privacy,
        schema=_load_check_summary(schema_path),
        business=_load_check_summary(business_path),
        quality=_load_check_summary(quality_path),
        monitoring=_load_check_summary(monitoring_path),
        execution_provenance=(
            "Valid · same run" if execution_valid else "Unavailable or mismatched"
        ),
        content_provenance=(
            "Recorded · same run" if content_current else "Unavailable or mismatched"
        ),
        source_fingerprint=_text(content, "source_content_fingerprint"),
        published_fingerprint=_text(content, "published_content_fingerprint"),
    )


def _decision_value(decision: str, severity: str | None = None) -> str:
    return f"{decision} / {severity}" if severity else decision


def _human_divergence_label(divergence_type: str) -> str:
    labels = {
        "agreement": "As avaliações inherent e residual estão de acordo",
        "residual_less_restrictive": "A avaliação residual é menos restritiva",
        "residual_more_restrictive": "A avaliação residual é mais restritiva",
        "unavailable": EVIDENCE_NOT_PERSISTED,
    }
    return labels.get(divergence_type, divergence_type)


def _is_unavailable(value: str) -> bool:
    return value.strip().casefold() in {
        "",
        "none",
        "unavailable",
        "unavailable or mismatched",
    }


def _check_summary_value(summary: CheckSummary) -> str:
    return summary.display if summary.total > 0 else VALIDATIONS_DEMONSTRATED


def _score_value(score: int | None) -> str:
    return str(score) if score is not None else "Não persistido"


def render_publication_governance(
    snapshot: PublicationGovernanceSnapshot | None = None,
) -> None:
    snapshot = snapshot or load_publication_governance_snapshot()

    st.header("Publication Governance")
    st.markdown(
        "Visão auditável das decisões de publicação, controles de privacidade, "
        "qualidade e evidências de governança."
    )
    st.caption(
        "Este ambiente público demonstra a arquitetura e os controles da "
        "plataforma. Algumas evidências operacionais dependem de execuções "
        "controladas e não são persistidas no deploy demonstrativo."
    )

    st.subheader("Decisão de publicação registrada")
    historical_decision = (
        EVIDENCE_NOT_PERSISTED
        if _is_unavailable(snapshot.historical_decision)
        else snapshot.historical_decision
    )
    render_metric_cards(
        [
            {
                "label": "Decisão histórica registrada",
                "value": historical_decision,
            },
        ],
        max_columns=1,
    )
    st.info(
        "Decisão histórica registrada e preservada como referência auditável."
    )

    st.subheader("Avaliações diagnósticas")
    diagnostics_available = (
        snapshot.inherent_score is not None
        and snapshot.residual_score is not None
        and not _is_unavailable(snapshot.shadow_decision)
        and not _is_unavailable(snapshot.residual_decision)
    )
    if diagnostics_available:
        render_metric_cards(
            [
                {
                    "label": "Diagnóstico shadow · inherent",
                    "value": (
                        f"{snapshot.inherent_score} → "
                        f"{_decision_value(snapshot.shadow_decision, snapshot.shadow_severity)}"
                    ),
                },
                {
                    "label": "Diagnóstico shadow · residual",
                    "value": (
                        f"{snapshot.residual_score} → "
                        f"{_decision_value(snapshot.residual_decision, snapshot.residual_severity)}"
                    ),
                },
            ],
            max_columns=2,
        )
        st.info(_human_divergence_label(snapshot.divergence_type))
    else:
        st.info(EVIDENCE_NOT_PERSISTED)
    st.caption(DIAGNOSTIC_NOTICE)

    st.subheader("Privacidade")
    protection = (
        f"Protegido — {snapshot.privacy.passed}/{snapshot.privacy.total} "
        "controles de privacidade aprovados"
        if snapshot.sensitive_data_protected is True
        else "Não protegido"
        if snapshot.sensitive_data_protected is False
        else "Evidência não persistida"
    )
    render_metric_cards(
        [
            {"label": "Score inherent", "value": _score_value(snapshot.inherent_score)},
            {"label": "Score residual", "value": _score_value(snapshot.residual_score)},
            {"label": "Proteção de dados sensíveis", "value": protection},
            {
                "label": "Controles de privacidade",
                "value": _check_summary_value(snapshot.privacy),
            },
        ]
    )
    st.caption(
        "A proteção é apresentada a partir da evidência persistida dos controles. "
        "O evaluator do pipeline permanece como fonte técnica desse indicador."
    )

    st.subheader("Qualidade e Governança")
    render_metric_cards(
        [
            {
                "label": "Contratos de esquema",
                "value": _check_summary_value(snapshot.schema),
            },
            {
                "label": "Regras de negócio",
                "value": _check_summary_value(snapshot.business),
            },
            {
                "label": "Qualidade dos dados",
                "value": _check_summary_value(snapshot.quality),
            },
            {
                "label": "Monitoramento",
                "value": _check_summary_value(snapshot.monitoring),
            },
        ]
    )

    st.subheader("Provenance")
    execution_provenance = (
        "Evidências vinculadas à mesma execução"
        if snapshot.execution_provenance == "Valid · same run"
        else "Evidência não persistida"
        if _is_unavailable(snapshot.execution_provenance)
        else snapshot.execution_provenance
    )
    content_provenance = (
        "Fingerprint do dataset registrado"
        if snapshot.content_provenance == "Recorded · same run"
        else "Evidência não persistida"
        if _is_unavailable(snapshot.content_provenance)
        else snapshot.content_provenance
    )
    render_metric_cards(
        [
            {
                "label": "Provenance de execução",
                "value": execution_provenance,
            },
            {
                "label": "Provenance de conteúdo",
                "value": content_provenance,
            },
        ],
        max_columns=2,
    )
    st.caption(
        "A proveniência de execução e conteúdo é registrada em execuções "
        "controladas. O deploy público não depende da persistência desses artefatos."
    )
    with st.expander("Detalhes técnicos e evidências", expanded=False):
        st.markdown(f"**Run ID:** `{snapshot.run_id}`")
        st.caption(f"Decisão histórica (raw): {snapshot.historical_decision}")
        st.caption(
            "Diagnóstico inherent (raw): "
            f"{snapshot.inherent_score} → "
            f"{_decision_value(snapshot.shadow_decision, snapshot.shadow_severity)}"
        )
        st.caption(
            "Diagnóstico residual (raw): "
            f"{snapshot.residual_score} → "
            f"{_decision_value(snapshot.residual_decision, snapshot.residual_severity)}"
        )
        st.caption(f"Divergência (raw): {snapshot.divergence_type}")
        st.caption(f"Provenance de execução (raw): {snapshot.execution_provenance}")
        st.caption(f"Provenance de conteúdo (raw): {snapshot.content_provenance}")
        st.markdown("**Fingerprint source**")
        st.code(snapshot.source_fingerprint)
        st.markdown("**Fingerprint published**")
        st.code(snapshot.published_fingerprint)
