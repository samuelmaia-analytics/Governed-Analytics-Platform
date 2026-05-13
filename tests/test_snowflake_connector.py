from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.snowflake_connector import SnowflakeConfig, SnowflakeConnector, _is_write_query


_SNOWFLAKE_ENVS = {
    "SNOWFLAKE_ACCOUNT": "test_account",
    "SNOWFLAKE_USER": "test_user",
    "SNOWFLAKE_PASSWORD": "test_password",
    "SNOWFLAKE_WAREHOUSE": "test_wh",
    "SNOWFLAKE_DATABASE": "test_db",
    "SNOWFLAKE_SCHEMA": "test_schema",
}


def _make_config() -> SnowflakeConfig:
    return SnowflakeConfig(
        account="acc",
        user="u",
        password="p",
        warehouse="wh",
        database="db",
        schema="sc",
    )


def _connector_with_mock_conn(mock_cursor_data: pd.DataFrame | None = None) -> tuple[SnowflakeConnector, MagicMock]:
    connector = SnowflakeConnector(_make_config())
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    if mock_cursor_data is not None:
        mock_cursor.fetch_pandas_all.return_value = mock_cursor_data
    mock_conn.cursor.return_value = mock_cursor
    connector._conn = mock_conn
    return connector, mock_cursor


# --- SnowflakeConfig ---


def test_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for k, v in _SNOWFLAKE_ENVS.items():
        monkeypatch.setenv(k, v)
    config = SnowflakeConfig.from_env()
    assert config.account == "test_account"
    assert config.database == "test_db"
    assert config.role == "PUBLIC"


def test_config_custom_role(monkeypatch: pytest.MonkeyPatch) -> None:
    for k, v in _SNOWFLAKE_ENVS.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("SNOWFLAKE_ROLE", "ANALYST")
    config = SnowflakeConfig.from_env()
    assert config.role == "ANALYST"


def test_config_missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in _SNOWFLAKE_ENVS:
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(EnvironmentError, match="Missing Snowflake env vars"):
        SnowflakeConfig.from_env()


# --- _is_write_query ---


@pytest.mark.parametrize("sql", [
    "DELETE FROM orders",
    "INSERT INTO t VALUES (1)",
    "UPDATE t SET x=1",
    "DROP TABLE t",
    "CREATE TABLE t (id INT)",
    "ALTER TABLE t ADD col INT",
    "TRUNCATE TABLE t",
    "MERGE INTO t USING s ON ...",
])
def test_is_write_query_true(sql: str) -> None:
    assert _is_write_query(sql) is True


@pytest.mark.parametrize("sql", [
    "SELECT * FROM orders",
    "select id from t",
    "  SELECT 1",
    "WITH cte AS (SELECT 1) SELECT * FROM cte",
])
def test_is_write_query_false(sql: str) -> None:
    assert _is_write_query(sql) is False


# --- SnowflakeConnector.health_check ---


def test_health_check_success() -> None:
    connector, mock_cursor = _connector_with_mock_conn()
    mock_cursor.fetchone.return_value = ("7.0.0",)

    result = connector.health_check()

    assert result["status"] == "connected"
    assert result["snowflake_version"] == "7.0.0"
    assert result["database"] == "db"


def test_health_check_failure() -> None:
    connector = SnowflakeConnector(_make_config())
    with patch("snowflake.connector.connect", side_effect=Exception("connection refused")):
        result = connector.health_check()
    assert result["status"] == "error"
    assert "connection refused" in result["detail"]


# --- SnowflakeConnector.query ---


def test_query_returns_dataframe() -> None:
    expected = pd.DataFrame({"col": [1, 2, 3]})
    connector, _ = _connector_with_mock_conn(mock_cursor_data=expected)
    result = connector.query("SELECT 1")
    pd.testing.assert_frame_equal(result, expected)


# --- SnowflakeConnector.list_tables ---


def test_list_tables_returns_entries() -> None:
    df = pd.DataFrame({"name": ["orders", "customers"]})
    connector, _ = _connector_with_mock_conn(mock_cursor_data=df)
    tables = connector.list_tables()
    assert len(tables) == 2
    assert tables[0]["table"] == "orders"
    assert tables[0]["database"] == "db"


def test_list_tables_empty() -> None:
    connector, _ = _connector_with_mock_conn(mock_cursor_data=pd.DataFrame())
    tables = connector.list_tables()
    assert tables == []


# --- context manager ---


def test_context_manager_closes_connection() -> None:
    connector = SnowflakeConnector(_make_config())
    mock_conn = MagicMock()
    with patch("snowflake.connector.connect", return_value=mock_conn):
        with connector:
            pass
    mock_conn.close.assert_called_once()
