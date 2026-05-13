from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.duckdb_engine import (
    DEFAULT_DUCKDB_PATH,
    ensure_database_parent_dir,
    execute_query,
    get_duckdb_version,
)


def test_get_duckdb_version_is_available() -> None:
    version = get_duckdb_version()
    assert version
    assert "." in version


def test_ensure_database_parent_dir_creates_folder(tmp_path: Path) -> None:
    db_file = tmp_path / "nested" / "db" / "test.duckdb"
    assert not db_file.parent.exists()

    resolved_path = ensure_database_parent_dir(db_file)

    assert resolved_path == db_file
    assert db_file.parent.exists()


def test_execute_query_returns_dataframe(tmp_path: Path) -> None:
    db_file = tmp_path / "query.duckdb"

    created = execute_query(
        "SELECT 1 AS metric, 'ok' AS status",
        db_path=db_file,
    )

    pd.testing.assert_frame_equal(
        created.reset_index(drop=True),
        pd.DataFrame({"metric": [1], "status": ["ok"]}),
        check_dtype=False,
    )


def test_default_duckdb_path_points_to_data_curated() -> None:
    assert DEFAULT_DUCKDB_PATH.as_posix() == "data/curated/analytics/governance.duckdb"
