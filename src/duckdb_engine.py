from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

DEFAULT_DUCKDB_PATH = Path("data/curated/analytics/governance.duckdb")


def ensure_database_parent_dir(db_path: Path | str = DEFAULT_DUCKDB_PATH) -> Path:
    resolved_path = Path(db_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def get_duckdb_version() -> str:
    return duckdb.__version__


def execute_query(
    query: str,
    db_path: Path | str = DEFAULT_DUCKDB_PATH,
    parameters: list[Any] | None = None,
) -> pd.DataFrame:
    resolved_path = ensure_database_parent_dir(db_path)
    with duckdb.connect(str(resolved_path)) as connection:
        if parameters is None:
            return connection.execute(query).df()
        return connection.execute(query, parameters).df()


def write_dataframe(
    dataframe: pd.DataFrame,
    table_name: str,
    db_path: Path | str = DEFAULT_DUCKDB_PATH,
) -> Path:
    resolved_path = ensure_database_parent_dir(db_path)
    with duckdb.connect(str(resolved_path)) as connection:
        connection.register("input_df", dataframe)
        connection.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM input_df")
        connection.unregister("input_df")
    return resolved_path
