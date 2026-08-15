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
    "Shadow and residual evaluations are diagnostic and do not replace the "
    "authoritative publication decision."
)


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
        "agreement": "The inherent and residual evaluations agree",
        "residual_less_restrictive": "Residual evaluation is less restrictive",
        "residual_more_restrictive": "Residual evaluation is more restrictive",
        "unavailable": "Comparison unavailable",
    }
    return labels.get(divergence_type, divergence_type)


def render_publication_governance(
    snapshot: PublicationGovernanceSnapshot | None = None,
) -> None:
    snapshot = snapshot or load_publication_governance_snapshot()

    st.header("Publication Governance")
    st.markdown(
        "The historical decision remains the publication authority. Shadow "
        "evaluations show how candidate privacy inputs behave without changing "
        "the official outcome."
    )

    st.subheader("Official publication decision")
    render_metric_cards(
        [
            {
                "label": "Historical · authoritative",
                "value": snapshot.historical_decision,
            },
        ],
        max_columns=1,
    )
    st.success(
        f"Authoritative decision: {snapshot.historical_decision}. This is the "
        "decision currently used by the platform."
    )

    st.subheader("Diagnostic / Shadow evaluations")
    render_metric_cards(
        [
            {
                "label": "Diagnostic / Shadow · inherent",
                "value": (
                    f"{snapshot.inherent_score} → "
                    f"{_decision_value(snapshot.shadow_decision, snapshot.shadow_severity)}"
                ),
            },
            {
                "label": "Diagnostic / Shadow · residual",
                "value": (
                    f"{snapshot.residual_score} → "
                    f"{_decision_value(snapshot.residual_decision, snapshot.residual_severity)}"
                ),
            },
        ],
        max_columns=2,
    )
    st.warning(DIAGNOSTIC_NOTICE)
    st.info(_human_divergence_label(snapshot.divergence_type))
    st.caption(f"Technical divergence type: `{snapshot.divergence_type}`")

    st.subheader("Privacy")
    protection = (
        f"Protected — {snapshot.privacy.passed}/{snapshot.privacy.total} "
        "privacy controls passed"
        if snapshot.sensitive_data_protected is True
        else "Not protected"
        if snapshot.sensitive_data_protected is False
        else "Unavailable"
    )
    render_metric_cards(
        [
            {"label": "Inherent score", "value": str(snapshot.inherent_score)},
            {"label": "Residual score", "value": str(snapshot.residual_score)},
            {"label": "Sensitive data protection", "value": protection},
            {"label": "Privacy checks", "value": snapshot.privacy.display},
        ]
    )
    st.caption(
        "Protection is displayed from the persisted privacy-control evidence; "
        "the pipeline evaluator remains authoritative for this input."
    )

    st.subheader("Quality & Governance")
    render_metric_cards(
        [
            {"label": "Schema checks", "value": snapshot.schema.display},
            {"label": "Business rules", "value": snapshot.business.display},
            {"label": "Quality checks", "value": snapshot.quality.display},
            {"label": "Monitoring", "value": snapshot.monitoring.display},
        ]
    )

    st.subheader("Provenance")
    execution_provenance = (
        "Evidence linked to the same execution"
        if snapshot.execution_provenance == "Valid · same run"
        else snapshot.execution_provenance
    )
    content_provenance = (
        "Dataset fingerprint recorded"
        if snapshot.content_provenance == "Recorded · same run"
        else snapshot.content_provenance
    )
    render_metric_cards(
        [
            {
                "label": "Execution provenance",
                "value": execution_provenance,
            },
            {
                "label": "Content provenance",
                "value": content_provenance,
            },
        ],
        max_columns=2,
    )
    with st.expander("Technical provenance details", expanded=False):
        st.markdown(f"**Run ID:** `{snapshot.run_id}`")
        st.caption(f"Execution provenance: {snapshot.execution_provenance}")
        st.caption(f"Content provenance: {snapshot.content_provenance}")
        st.markdown("**Source fingerprint**")
        st.code(snapshot.source_fingerprint)
        st.markdown("**Published fingerprint**")
        st.code(snapshot.published_fingerprint)
