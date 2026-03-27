from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.run_analytics_queries as analytics_queries


class FakeQueryResult:
    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df

    def fetchdf(self) -> pd.DataFrame:
        return self._df


class FakeConnection:
    def __init__(self, df: pd.DataFrame | None = None) -> None:
        self.df = df if df is not None else pd.DataFrame({"metric": [1], "value": [10.0]})
        self.executed_sql: list[str] = []
        self.closed = False

    def execute(self, sql: str) -> FakeQueryResult:
        self.executed_sql.append(sql)
        return FakeQueryResult(self.df)

    def close(self) -> None:
        self.closed = True


def test_validate_inputs_returns_sorted_sql_files(tmp_path: Path, monkeypatch) -> None:
    table_path = tmp_path / "fact.parquet"
    query_dir = tmp_path / "sql"
    table_path.write_text("placeholder", encoding="utf-8")
    query_dir.mkdir()
    (query_dir / "02_query.sql").write_text("select 2", encoding="utf-8")
    (query_dir / "01_query.sql").write_text("select 1", encoding="utf-8")

    monkeypatch.setattr(analytics_queries, "ANALYTICS_TABLE_PATH", table_path)
    monkeypatch.setattr(analytics_queries, "QUERY_DIR", query_dir)

    sql_files = analytics_queries.validate_inputs()

    assert [path.name for path in sql_files] == ["01_query.sql", "02_query.sql"]


def test_validate_inputs_raises_when_sql_directory_is_empty(tmp_path: Path, monkeypatch) -> None:
    table_path = tmp_path / "fact.parquet"
    query_dir = tmp_path / "sql"
    table_path.write_text("placeholder", encoding="utf-8")
    query_dir.mkdir()

    monkeypatch.setattr(analytics_queries, "ANALYTICS_TABLE_PATH", table_path)
    monkeypatch.setattr(analytics_queries, "QUERY_DIR", query_dir)

    with pytest.raises(FileNotFoundError):
        analytics_queries.validate_inputs()


def test_connect_raises_clear_error_when_duckdb_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(analytics_queries, "duckdb", None)
    monkeypatch.setattr(analytics_queries, "DUCKDB_IMPORT_ERROR", ImportError("missing duckdb"))

    with pytest.raises(ImportError):
        analytics_queries.connect()


def test_execute_query_exports_csv_and_returns_metadata(tmp_path: Path, monkeypatch) -> None:
    output_dir = tmp_path / "out"
    sql_path = tmp_path / "monthly_revenue.sql"
    sql_path.write_text("select 1 as metric, 2 as value", encoding="utf-8")
    connection = FakeConnection(pd.DataFrame({"metric": [1], "value": [2]}))

    monkeypatch.setattr(analytics_queries, "OUTPUT_DIR", output_dir)

    result = analytics_queries.execute_query(connection, sql_path)

    assert result.query_name == "monthly_revenue"
    assert result.row_count == 1
    assert result.column_count == 2
    assert result.output_path.exists()
    assert "select 1 as metric" in connection.executed_sql[0]


def test_execute_query_rejects_empty_sql_file(tmp_path: Path) -> None:
    sql_path = tmp_path / "empty.sql"
    sql_path.write_text("   ", encoding="utf-8")

    with pytest.raises(ValueError):
        analytics_queries.execute_query(FakeConnection(), sql_path)


def test_run_queries_executes_all_sql_files_and_closes_connection(tmp_path: Path, monkeypatch) -> None:
    query_a = tmp_path / "01_a.sql"
    query_b = tmp_path / "02_b.sql"
    query_a.write_text("select 1 as metric", encoding="utf-8")
    query_b.write_text("select 2 as metric", encoding="utf-8")
    connection = FakeConnection()

    monkeypatch.setattr(analytics_queries, "validate_inputs", lambda: [query_a, query_b])
    monkeypatch.setattr(analytics_queries, "connect", lambda: connection)
    monkeypatch.setattr(analytics_queries, "OUTPUT_DIR", tmp_path / "out")

    results = analytics_queries.run_queries()

    assert [result.query_name for result in results] == ["01_a", "02_b"]
    assert connection.closed is True


def test_save_execution_manifest_persists_normalized_paths(tmp_path: Path, monkeypatch) -> None:
    output_dir = tmp_path / "out"
    monkeypatch.setattr(analytics_queries, "OUTPUT_DIR", output_dir)

    manifest_path = analytics_queries.save_execution_manifest(
        [
            analytics_queries.QueryExecutionResult(
                query_name="demo",
                sql_path=Path(r"C:\repo\sql\demo.sql"),
                output_path=Path(r"C:\repo\data\demo.csv"),
                row_count=10,
                column_count=2,
            )
        ]
    )

    manifest_df = pd.read_csv(manifest_path)

    assert manifest_path.exists()
    assert manifest_df.loc[0, "sql_path"] == "C:/repo/sql/demo.sql"
    assert manifest_df.loc[0, "output_path"] == "C:/repo/data/demo.csv"
