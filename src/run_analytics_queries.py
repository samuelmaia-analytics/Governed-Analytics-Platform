from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import ANALYTICS_DIR, QUERY_RESULTS_DIR, SQL_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

try:
    import duckdb
except ImportError as exc:  # pragma: no cover - depends on local environment
    duckdb = None
    DUCKDB_IMPORT_ERROR = exc
else:
    DUCKDB_IMPORT_ERROR = None


LOGGER = logging.getLogger(__name__)
ANALYTICS_TABLE_PATH = ANALYTICS_DIR / "fact_orders_enriched.parquet"
QUERY_DIR = SQL_DIR / "analytics"
OUTPUT_DIR = QUERY_RESULTS_DIR


@dataclass
class QueryExecutionResult:
    query_name: str
    sql_path: Path
    output_path: Path
    row_count: int
    column_count: int


def validate_inputs() -> list[Path]:
    if not ANALYTICS_TABLE_PATH.exists():
        raise FileNotFoundError(f"Tabela analitica nao encontrada: {ANALYTICS_TABLE_PATH}")

    sql_files = sorted(QUERY_DIR.glob("*.sql"))
    if not sql_files:
        raise FileNotFoundError(f"Nenhuma query SQL encontrada em: {QUERY_DIR}")

    return sql_files


def connect() -> duckdb.DuckDBPyConnection:
    if duckdb is None:
        raise ImportError(
            "DuckDB nao esta instalado no ambiente atual. "
            "Instale com `pip install duckdb` ou `pip install -r requirements.txt`."
        ) from DUCKDB_IMPORT_ERROR

    connection = duckdb.connect(database=":memory:")
    parquet_path = str(ANALYTICS_TABLE_PATH).replace("\\", "/").replace("'", "''")
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW fact_orders_enriched AS
        SELECT *
        FROM read_parquet('{parquet_path}')
        """
    )
    return connection


def execute_query(
    connection: duckdb.DuckDBPyConnection,
    sql_path: Path,
) -> QueryExecutionResult:
    query_sql = sql_path.read_text(encoding="utf-8").strip()
    if not query_sql:
        raise ValueError(f"Arquivo SQL vazio: {sql_path}")

    LOGGER.info("Executando query: %s", sql_path.name)
    result_df = connection.execute(query_sql).fetchdf()

    ensure_directory(OUTPUT_DIR)
    output_path = OUTPUT_DIR / f"{sql_path.stem}.csv"
    result_df.to_csv(output_path, index=False)

    LOGGER.info(
        "Resultado exportado: %s | shape=(%s, %s)",
        output_path.name,
        result_df.shape[0],
        result_df.shape[1],
    )
    return QueryExecutionResult(
        query_name=sql_path.stem,
        sql_path=sql_path,
        output_path=output_path,
        row_count=int(result_df.shape[0]),
        column_count=int(result_df.shape[1]),
    )


def run_queries() -> list[QueryExecutionResult]:
    sql_files = validate_inputs()
    connection = connect()

    try:
        results = [execute_query(connection, sql_path) for sql_path in sql_files]
    finally:
        connection.close()

    return results


def save_execution_manifest(results: list[QueryExecutionResult]) -> Path:
    ensure_directory(OUTPUT_DIR)
    manifest_path = OUTPUT_DIR / "query_execution_manifest.csv"
    manifest_df = pd.DataFrame(
        [
            {
                "query_name": result.query_name,
                "sql_path": str(result.sql_path).replace("\\", "/"),
                "output_path": str(result.output_path).replace("\\", "/"),
                "row_count": result.row_count,
                "column_count": result.column_count,
            }
            for result in results
        ]
    )
    manifest_df.to_csv(manifest_path, index=False)
    LOGGER.info("Manifesto salvo em %s", manifest_path)
    return manifest_path


def main() -> None:
    configure_logging()
    results = run_queries()
    save_execution_manifest(results)


if __name__ == "__main__":
    main()
