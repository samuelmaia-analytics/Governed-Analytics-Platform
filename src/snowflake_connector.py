from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class SnowflakeConfig:
    account: str
    user: str
    password: str
    warehouse: str
    database: str
    schema: str
    role: str = "PUBLIC"

    @classmethod
    def from_env(cls) -> "SnowflakeConfig":
        required = (
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_WAREHOUSE",
            "SNOWFLAKE_DATABASE",
            "SNOWFLAKE_SCHEMA",
        )
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            raise EnvironmentError(f"Missing Snowflake env vars: {', '.join(missing)}")
        return cls(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ["SNOWFLAKE_PASSWORD"],
            warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
            database=os.environ["SNOWFLAKE_DATABASE"],
            schema=os.environ["SNOWFLAKE_SCHEMA"],
            role=os.getenv("SNOWFLAKE_ROLE", "PUBLIC"),
        )


_WRITE_PREFIXES = ("INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE", "MERGE")


def _is_write_query(sql: str) -> bool:
    return sql.strip().upper().split()[0] in _WRITE_PREFIXES


class SnowflakeConnector:
    def __init__(self, config: SnowflakeConfig) -> None:
        self._config = config
        self._conn: Any = None

    def connect(self) -> None:
        import snowflake.connector  # lazy import — optional dependency

        self._conn = snowflake.connector.connect(
            account=self._config.account,
            user=self._config.user,
            password=self._config.password,
            warehouse=self._config.warehouse,
            database=self._config.database,
            schema=self._config.schema,
            role=self._config.role,
        )

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "SnowflakeConnector":
        self.connect()
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def query(self, sql: str) -> pd.DataFrame:
        if not self._conn:
            self.connect()
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetch_pandas_all()
        finally:
            cursor.close()

    def list_tables(self) -> list[dict[str, str]]:
        df = self.query(
            f"SHOW TABLES IN SCHEMA {self._config.database}.{self._config.schema}"
        )
        if df.empty:
            return []
        name_col = "name" if "name" in df.columns else df.columns[1]
        return [
            {
                "table": str(row[name_col]),
                "database": self._config.database,
                "schema": self._config.schema,
            }
            for _, row in df.iterrows()
        ]

    def health_check(self) -> dict[str, Any]:
        try:
            if not self._conn:
                self.connect()
            cursor = self._conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()
            return {
                "status": "connected",
                "snowflake_version": version,
                "account": self._config.account,
                "database": self._config.database,
                "schema": self._config.schema,
            }
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}


def get_snowflake_connector() -> SnowflakeConnector:
    config = SnowflakeConfig.from_env()
    return SnowflakeConnector(config)
