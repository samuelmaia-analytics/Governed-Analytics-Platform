from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI

from src.config import PUBLISHED_MONITORING_DIR

PUBLICATION_DECISION_PATH = PUBLISHED_MONITORING_DIR / "publication_decision.json"
SCHEMA_CONTRACT_RESULTS_PATH = Path("data/curated/quality/schema_contract_results.csv")
PUBLISHED_MONITORING_RESULTS_PATH = (
    PUBLISHED_MONITORING_DIR / "published_layer_monitoring.csv"
)

app = FastAPI(title="Governed Analytics Platform API", version="1.0.0")


def _load_publication_decision(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _schema_contract_status(path: Path) -> str:
    if not path.exists():
        return "unknown"
    try:
        checks_df = pd.read_csv(path)
    except Exception:
        return "unknown"
    if checks_df.empty or "status" not in checks_df.columns:
        return "unknown"
    has_failures = checks_df["status"].astype(str).str.upper().eq("FAIL").any()
    return "failed" if has_failures else "passed"


def _freshness_status(path: Path) -> str:
    if not path.exists():
        return "unknown"
    try:
        checks_df = pd.read_csv(path)
    except Exception:
        return "unknown"
    if checks_df.empty or "check_name" not in checks_df.columns:
        return "unknown"
    freshness_rows = checks_df[
        checks_df["check_name"].astype(str) == "published_file_freshness_hours"
    ]
    if freshness_rows.empty:
        return "unknown"
    row = freshness_rows.iloc[-1]
    status = str(row.get("status", "")).upper()
    if status == "PASS":
        return "fresh"
    metric_value = pd.to_numeric(row.get("metric_value"), errors="coerce")
    threshold = pd.to_numeric(row.get("threshold"), errors="coerce")
    if pd.notna(metric_value) and pd.notna(threshold) and float(metric_value) <= float(
        threshold
    ) * 1.5:
        return "warning"
    return "stale"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/governance/status")
def governance_status() -> dict[str, Any]:
    decision = _load_publication_decision(PUBLICATION_DECISION_PATH)
    return {
        "dataset": decision.get("dataset", "fact_orders_dashboard"),
        "publication_status": decision.get("status", "unknown"),
        "data_quality_score": int(decision.get("quality_score", 0)),
        "privacy_risk_score": int(decision.get("privacy_risk_score", 0)),
        "failed_checks": int(decision.get("failed_checks", 0)),
        "schema_contract_status": _schema_contract_status(SCHEMA_CONTRACT_RESULTS_PATH),
        "freshness_status": _freshness_status(PUBLISHED_MONITORING_RESULTS_PATH),
        "decision_reason": decision.get("decision_reason", "No decision artifact found."),
        "timestamp_utc": decision.get(
            "timestamp_utc", datetime.now(timezone.utc).isoformat()
        ),
    }
