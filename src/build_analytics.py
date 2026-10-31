from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.analytics.olist.aggregations import build_payments_agg, build_reviews_agg
from src.analytics.olist.cleaning import (
    clean_customers,
    clean_order_items,
    clean_orders,
    clean_products,
    clean_sellers,
    clean_translation,
    convert_datetime_columns,
    deduplicate,
    standardize_columns,
    to_snake_case,
)
from src.analytics.olist.loaders import read_olist_table as _read_olist_table
from src.analytics.olist.mart import (
    build_fact_orders_enriched as _build_fact_orders_enriched,
)
from src.analytics.olist.outputs import (
    BuildArtifacts,
)
from src.analytics.olist.outputs import (
    render_report as _render_report,
)
from src.analytics.olist.outputs import (
    save_outputs as _save_outputs,
)
from src.analytics.olist.outputs import (
    save_report as _save_report,
)
from src.analytics.olist.pipeline import run_build as _run_build
from src.analytics.olist.reconciliation import (
    build_join_health_summary,
    build_payment_reconciliation_summary,
)
from src.analytics.olist.transformations import (
    derive_columns,
    remove_obvious_inconsistencies,
    select_output_columns,
)
from src.config import ANALYTICS_DIR, DOCS_DIR, LANDING_DIR, STANDARDIZED_DIR
from src.duckdb_engine import write_dataframe
from src.ingest import configure_logging, load_csv
from src.quality import validate_not_empty

__all__ = [
    "BuildArtifacts",
    "build_fact_orders_enriched",
    "build_join_health_summary",
    "build_payment_reconciliation_summary",
    "build_payments_agg",
    "build_reviews_agg",
    "clean_customers",
    "clean_order_items",
    "clean_orders",
    "clean_products",
    "clean_sellers",
    "clean_translation",
    "convert_datetime_columns",
    "deduplicate",
    "derive_columns",
    "read_olist_table",
    "remove_obvious_inconsistencies",
    "render_report",
    "run_build",
    "save_outputs",
    "save_report",
    "select_output_columns",
    "standardize_columns",
    "to_snake_case",
]

LOGGER = logging.getLogger(__name__)
OLIST_LANDING_DIR = LANDING_DIR / "olist"
STANDARDIZED_OLIST_DIR = STANDARDIZED_DIR / "olist"
FACT_PARQUET_PATH = ANALYTICS_DIR / "fact_orders_enriched.parquet"
FACT_CSV_PATH = ANALYTICS_DIR / "fact_orders_enriched.csv"
FACT_DUCKDB_PATH = ANALYTICS_DIR / "governance.duckdb"
FACT_DUCKDB_TABLE = "fact_orders_enriched"
REPORT_PATH = DOCS_DIR / "fact_orders_enriched.md"


def read_olist_table(file_name: str) -> pd.DataFrame:
    return _read_olist_table(
        file_name,
        standardized_dir=STANDARDIZED_OLIST_DIR,
        landing_dir=OLIST_LANDING_DIR,
        load_csv_fn=load_csv,
        logger=LOGGER,
    )


def build_fact_orders_enriched() -> pd.DataFrame:
    return _build_fact_orders_enriched(
        read_table_fn=read_olist_table,
        validate_not_empty_fn=validate_not_empty,
        logger=LOGGER,
    )


def save_outputs(fact_table: pd.DataFrame) -> tuple[Path, Path, Path]:
    return _save_outputs(
        fact_table,
        analytics_dir=ANALYTICS_DIR,
        parquet_path=FACT_PARQUET_PATH,
        csv_path=FACT_CSV_PATH,
        duckdb_path=FACT_DUCKDB_PATH,
        duckdb_table=FACT_DUCKDB_TABLE,
        write_dataframe_fn=write_dataframe,
        logger=LOGGER,
    )


def render_report(fact_table: pd.DataFrame) -> str:
    return _render_report(fact_table)


def save_report(fact_table: pd.DataFrame) -> Path:
    return _save_report(
        fact_table,
        docs_dir=DOCS_DIR,
        report_path=REPORT_PATH,
        render_report_fn=render_report,
        logger=LOGGER,
    )


def run_build() -> BuildArtifacts:
    return _run_build(
        build_fact_fn=build_fact_orders_enriched,
        save_outputs_fn=save_outputs,
        save_report_fn=save_report,
    )


if __name__ == "__main__":
    configure_logging()
    run_build()
