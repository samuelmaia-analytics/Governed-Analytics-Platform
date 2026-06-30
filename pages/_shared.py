from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

QUALITY_CHECKS_PATH = (
    PROJECT_ROOT / "data/curated/quality/fact_orders_enriched_quality_checks.csv"
)
PUBLISHED_MONITORING_PATH = (
    PROJECT_ROOT / "data/published/monitoring/published_layer_monitoring.csv"
)
GOVERNANCE_SCORECARDS_PATH = (
    PROJECT_ROOT / "data/published/monitoring/governance_scorecards.csv"
)
DATA_CLASSIFICATION_PATH = (
    PROJECT_ROOT / "data/curated/catalog/data_classification_inventory.csv"
)
SCHEMA_CONTRACT_RESULTS_PATH = (
    PROJECT_ROOT / "data/curated/quality/schema_contract_results.csv"
)
SCHEMA_CONTRACT_REPORT_PATH = PROJECT_ROOT / "docs/reports/schema_contract_report.md"
BUSINESS_RULE_RESULTS_PATH = (
    PROJECT_ROOT / "data/curated/quality/business_rule_results.csv"
)
PIPELINE_LOG_PATH = PROJECT_ROOT / "logs/pipeline_execution_logs.csv"
PRIVACY_RISK_PATH = PROJECT_ROOT / "logs/privacy_risk_score.json"
PUBLICATION_DECISION_PATH = (
    PROJECT_ROOT / "data/published/monitoring/publication_decision.json"
)
DOCS_DIR = PROJECT_ROOT / "docs"
WORKFLOWS_DIR = PROJECT_ROOT / "workflows/n8n"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"


@st.cache_data(show_spinner=False)
def read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - visible in Streamlit runtime
        st.warning(f"Could not read `{path.as_posix()}`: {exc}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def read_json_safe(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - visible in Streamlit runtime
        st.warning(f"Could not read `{path.as_posix()}`: {exc}")
        return {}


@st.cache_data(show_spinner=False)
def read_text_safe(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")
    except Exception as exc:  # pragma: no cover - visible in Streamlit runtime
        st.warning(f"Could not read `{path.as_posix()}`: {exc}")
        return ""


def read_first_csv(paths: list[Path]) -> tuple[pd.DataFrame, Path | None]:
    for path in paths:
        df = read_csv_safe(path)
        if not df.empty:
            return df, path
    return pd.DataFrame(), None


def read_first_json(paths: list[Path]) -> tuple[dict[str, Any], Path | None]:
    for path in paths:
        payload = read_json_safe(path)
        if payload:
            return payload, path
    return {}, None


def read_schema_contract_results() -> tuple[pd.DataFrame, Path | None]:
    csv_df = read_csv_safe(SCHEMA_CONTRACT_RESULTS_PATH)
    if not csv_df.empty:
        return csv_df, SCHEMA_CONTRACT_RESULTS_PATH

    content = read_text_safe(SCHEMA_CONTRACT_REPORT_PATH)
    if not content:
        return pd.DataFrame(), None

    rows: list[dict[str, str]] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        cells = [
            cell.strip().strip("`").strip("*")
            for cell in stripped.strip("|").split("|")
        ]
        if len(cells) < 4:
            continue
        dataset, check_name, status = cells[:3]
        details = " | ".join(cells[3:])
        rows.append(
            {
                "dataset_name": dataset,
                "layer": "",
                "check_name": check_name,
                "status": status,
                "details": details,
            }
        )
    return pd.DataFrame(rows), SCHEMA_CONTRACT_REPORT_PATH if rows else None


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def file_status(label: str, path: Path) -> dict[str, Any]:
    exists = path.exists()
    size = path.stat().st_size if exists and path.is_file() else 0
    return {
        "artifact": label,
        "path": relative_path(path),
        "status": "available" if exists else "missing",
        "size_bytes": size,
    }


def render_file_warning(path: Path, guidance: str) -> None:
    st.info(
        f"`{relative_path(path)}` was not found. {guidance} "
        "The dashboard is using a safe fallback and no synthetic evidence is shown."
    )


def count_statuses(df: pd.DataFrame, column: str = "status") -> dict[str, int]:
    if df.empty or column not in df.columns:
        return {}
    return {
        str(key).upper(): int(value)
        for key, value in df[column].fillna("unknown").value_counts().items()
    }


def format_datetime(value: Any) -> str:
    if value is None or str(value).strip() == "":
        return ""
    try:
        parsed = pd.to_datetime(value)
        if pd.isna(parsed):
            return str(value)
        return parsed.strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    except Exception:
        try:
            return datetime.fromisoformat(str(value)).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return str(value)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    normalized = df.copy()
    normalized.columns = [str(col).strip() for col in normalized.columns]
    return normalized


def markdown_files() -> list[Path]:
    if not DOCS_DIR.exists():
        return []
    return sorted(DOCS_DIR.rglob("*.md"), key=lambda path: relative_path(path).lower())
