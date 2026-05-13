from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import src.api as api


def _mock_connector(
    *,
    health: dict | None = None,
    tables: list | None = None,
    query_df: pd.DataFrame | None = None,
) -> MagicMock:
    mock = MagicMock()
    if health is not None:
        mock.health_check.return_value = health
    if tables is not None:
        mock.list_tables.return_value = tables
    if query_df is not None:
        mock.query.return_value = query_df
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


# --- /api/v1/snowflake/health ---


def test_snowflake_health_connected(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = _mock_connector(health={"status": "connected", "snowflake_version": "7.0"})
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)
    client = TestClient(api.app)
    response = client.get("/api/v1/snowflake/health")
    assert response.status_code == 200
    assert response.json()["status"] == "connected"


def test_snowflake_health_error(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = _mock_connector(health={"status": "error", "detail": "timeout"})
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)
    client = TestClient(api.app)
    response = client.get("/api/v1/snowflake/health")
    assert response.status_code == 200
    assert response.json()["status"] == "error"


# --- /api/v1/snowflake/tables ---


def test_snowflake_tables(monkeypatch: pytest.MonkeyPatch) -> None:
    tables = [{"table": "orders", "database": "db", "schema": "sc"}]
    mock = _mock_connector(tables=tables)
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)
    client = TestClient(api.app)
    response = client.get("/api/v1/snowflake/tables")
    assert response.status_code == 200
    assert response.json()[0]["table"] == "orders"


def test_snowflake_tables_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = _mock_connector(tables=[])
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)
    client = TestClient(api.app)
    response = client.get("/api/v1/snowflake/tables")
    assert response.status_code == 200
    assert response.json() == []


# --- /api/v1/snowflake/query ---


def test_snowflake_query_select(monkeypatch: pytest.MonkeyPatch) -> None:
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
    mock = _mock_connector(query_df=df)
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)
    client = TestClient(api.app)
    response = client.post("/api/v1/snowflake/query", json={"sql": "SELECT * FROM orders"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["row_count"] == 2
    assert "id" in payload["columns"]
    assert payload["rows"][0]["id"] == 1


@pytest.mark.parametrize("sql", [
    "DELETE FROM orders",
    "INSERT INTO t VALUES (1)",
    "UPDATE t SET x=1",
    "DROP TABLE t",
    "TRUNCATE TABLE t",
])
def test_snowflake_query_rejects_write(sql: str) -> None:
    client = TestClient(api.app)
    response = client.post("/api/v1/snowflake/query", json={"sql": sql})
    assert response.status_code == 400
    assert "SELECT" in response.json()["detail"]
