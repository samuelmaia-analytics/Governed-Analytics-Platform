from __future__ import annotations

import ast
import importlib
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
from fastapi.testclient import TestClient

from app import context
from src import api

ROOT = Path(__file__).resolve().parents[1]


def _page_paths(entrypoint: Path) -> list[str]:
    tree = ast.parse(entrypoint.read_text(encoding="utf-8"))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and (node.value.startswith("pages/") or node.value.startswith("app.pages."))
    ]


def test_canonical_streamlit_entrypoint_and_pages_remain_available() -> None:
    module = importlib.import_module("app.main")
    assert callable(module.main)
    expected_modules = {
        "cohort_retention", "data_catalog", "data_quality", "eda",
        "executive_overview", "genai_insights", "governance_control_center",
        "governance_report", "lgpd_privacy_risk", "n8n_automation",
        "revenue_analytics", "seller_performance", "snowflake_explorer",
    }
    assert expected_modules.issubset({p.stem for p in (ROOT / "app" / "pages").glob("*.py")})


def test_complementary_streamlit_entrypoint_and_pages_remain_available() -> None:
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    compile(source, str(ROOT / "app.py"), "exec")
    expected = {f"{number:02d}_{name}.py" for number, name in enumerate([
        "Overview", "Data_Quality", "LGPD_Risk", "Data_Contracts",
        "Pipeline_Logs", "n8n_Automation", "Governance_Docs",
        "Operational_Health", "AWS_Architecture",
    ], start=1)}
    assert expected == {p.name for p in (ROOT / "pages").glob("[0-9][0-9]_*.py")}
    assert (ROOT / "streamlit_shared.py").is_file()


def test_streamlit_loader_prefers_published_and_preserves_sample_fallback(monkeypatch, tmp_path: Path) -> None:
    published = tmp_path / "published.csv"
    sample = tmp_path / "sample.csv"
    pd.DataFrame({"source": ["published"]}).to_csv(published, index=False)
    pd.DataFrame({"source": ["sample"]}).to_csv(sample, index=False)
    monkeypatch.setattr(context, "DEFAULT_PUBLISHED_DATASET", published)
    monkeypatch.setattr(context, "DEFAULT_SAMPLE_DATASET", sample)
    monkeypatch.setattr(context.st.sidebar, "file_uploader", lambda *a, **k: None)
    monkeypatch.setattr(context.st.sidebar, "toggle", lambda *a, **k: True)
    monkeypatch.setattr(context.st.sidebar, "header", lambda *a, **k: None)
    monkeypatch.setattr(context.st.sidebar, "caption", lambda *a, **k: None)
    assert context.load_input_dataframe("en-US")["source"].iloc[0] == "published"
    published.unlink()
    assert context.load_input_dataframe("en-US")["source"].iloc[0] == "sample"
    assert "curated/analytics" not in context.DEFAULT_PUBLISHED_DATASET.as_posix()


def test_api_payload_and_missing_artifact_behavior(tmp_path: Path, monkeypatch) -> None:
    decision = tmp_path / "decision.json"
    schema = tmp_path / "schema.csv"
    monitoring = tmp_path / "monitoring.csv"
    decision.write_text('{"dataset":"fact_orders_dashboard","status":"Approved","quality_score":97,"privacy_risk_score":18,"failed_checks":0,"decision_reason":"baseline","timestamp_utc":"2026-01-01T00:00:00+00:00"}', encoding="utf-8")
    pd.DataFrame({"status": ["PASS"]}).to_csv(schema, index=False)
    pd.DataFrame({"check_name": ["published_file_freshness_hours"], "status": ["PASS"], "metric_value": [1], "threshold": [36]}).to_csv(monitoring, index=False)
    monkeypatch.setattr(api, "PUBLICATION_DECISION_PATH", decision)
    monkeypatch.setattr(api, "SCHEMA_CONTRACT_RESULTS_PATH", schema)
    monkeypatch.setattr(api, "PUBLISHED_MONITORING_RESULTS_PATH", monitoring)
    client = TestClient(api.app)
    assert client.get("/health").json() == {"status": "ok"}
    payload = client.get("/api/v1/governance/status").json()
    assert payload == {"dataset": "fact_orders_dashboard", "publication_status": "Approved", "data_quality_score": 97, "privacy_risk_score": 18, "failed_checks": 0, "schema_contract_status": "passed", "freshness_status": "fresh", "decision_reason": "baseline", "timestamp_utc": "2026-01-01T00:00:00+00:00"}
    monkeypatch.setattr(api, "PUBLICATION_DECISION_PATH", tmp_path / "missing-decision.json")
    monkeypatch.setattr(api, "SCHEMA_CONTRACT_RESULTS_PATH", tmp_path / "missing-schema.csv")
    monkeypatch.setattr(api, "PUBLISHED_MONITORING_RESULTS_PATH", tmp_path / "missing-monitoring.csv")
    missing = client.get("/api/v1/governance/status").json()
    assert missing["publication_status"] == "unknown"
    assert missing["schema_contract_status"] == "unknown"
    assert missing["freshness_status"] == "unknown"


def test_snowflake_api_closes_health_connection_and_context_manages_queries(monkeypatch) -> None:
    connector = MagicMock()
    connector.health_check.return_value = {"status": "connected"}
    connector.__enter__.return_value = connector
    connector.list_tables.return_value = [{"table": "ORDERS", "database": "DB", "schema": "PUBLIC"}]
    connector.query.return_value = pd.DataFrame({"value": [1]})
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: connector)
    client = TestClient(api.app)
    assert client.get("/api/v1/snowflake/health").json() == {"status": "connected"}
    connector.close.assert_called_once_with()
    assert client.get("/api/v1/snowflake/tables").json()[0]["table"] == "ORDERS"
    assert client.post("/api/v1/snowflake/query", json={"sql": "SELECT 1"}).json() == {"columns": ["value"], "rows": [{"value": 1}], "row_count": 1}
    assert connector.__exit__.call_count == 2
