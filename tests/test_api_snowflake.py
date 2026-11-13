from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import src.api as api


def _set_bearer_token(monkeypatch: pytest.MonkeyPatch, token: str = "token") -> dict[str, str]:
    monkeypatch.setenv("GAP_API_BEARER_TOKEN", token)
    return {"Authorization": f"Bearer {token}"}


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


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/snowflake/health"),
        ("GET", "/api/v1/snowflake/tables"),
        ("POST", "/api/v1/snowflake/query"),
    ],
)
def test_snowflake_endpoints_require_auth_by_default(
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    path: str,
) -> None:
    headers = _set_bearer_token(monkeypatch)
    df = pd.DataFrame({"id": [1]})
    mock = _mock_connector(
        health={"status": "connected"},
        tables=[{"table": "orders", "database": "db", "schema": "sc"}],
        query_df=df,
    )
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)

    client = TestClient(api.app)

    if method == "POST":
        response = client.request(method, path, json={"sql": "SELECT 1"})
        assert response.status_code == 401
        response = client.request(method, path, headers=headers, json={"sql": "SELECT 1"})
        assert response.status_code == 200
    else:
        response = client.request(method, path)
        assert response.status_code == 401
        response = client.request(method, path, headers=headers)
        assert response.status_code == 200


def test_snowflake_health_connected(monkeypatch: pytest.MonkeyPatch) -> None:
    headers = _set_bearer_token(monkeypatch)
    mock = _mock_connector(health={"status": "connected", "snowflake_version": "7.0"})
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)

    client = TestClient(api.app)
    response = client.get("/api/v1/snowflake/health", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "connected"


def test_snowflake_health_error(monkeypatch: pytest.MonkeyPatch) -> None:
    headers = _set_bearer_token(monkeypatch)
    mock = _mock_connector(health={"status": "error", "detail": "timeout"})
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)

    client = TestClient(api.app)
    response = client.get("/api/v1/snowflake/health", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "error"


def test_snowflake_tables(monkeypatch: pytest.MonkeyPatch) -> None:
    headers = _set_bearer_token(monkeypatch)
    tables = [{"table": "orders", "database": "db", "schema": "sc"}]
    mock = _mock_connector(tables=tables)
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)

    client = TestClient(api.app)
    response = client.get("/api/v1/snowflake/tables", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["table"] == "orders"


def test_snowflake_tables_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    headers = _set_bearer_token(monkeypatch)
    mock = _mock_connector(tables=[])
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)

    client = TestClient(api.app)
    response = client.get("/api/v1/snowflake/tables", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_snowflake_query_select(monkeypatch: pytest.MonkeyPatch) -> None:
    headers = _set_bearer_token(monkeypatch)
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
    mock = _mock_connector(query_df=df)
    monkeypatch.setattr(api, "get_snowflake_connector", lambda: mock)

    client = TestClient(api.app)
    response = client.post(
        "/api/v1/snowflake/query",
        json={"sql": "SELECT * FROM orders"},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["row_count"] == 2
    assert "id" in payload["columns"]
    assert payload["rows"][0]["id"] == 1


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM orders",
        "INSERT INTO t VALUES (1)",
        "UPDATE t SET x=1",
        "DROP TABLE t",
        "TRUNCATE TABLE t",
    ],
)
def test_snowflake_query_rejects_write(monkeypatch: pytest.MonkeyPatch, sql: str) -> None:
    headers = _set_bearer_token(monkeypatch)
    client = TestClient(api.app)
    response = client.post(
        "/api/v1/snowflake/query",
        json={"sql": sql},
        headers=headers,
    )
    assert response.status_code == 400
    assert "SELECT" in response.json()["detail"]
