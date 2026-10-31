"""Olist analytics transformations used by the compatibility facade."""

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
from src.analytics.olist.loaders import read_olist_table
from src.analytics.olist.mart import build_fact_orders_enriched
from src.analytics.olist.outputs import BuildArtifacts, render_report
from src.analytics.olist.pipeline import run_build
from src.analytics.olist.reconciliation import (
    build_join_health_summary,
    build_payment_reconciliation_summary,
)
from src.analytics.olist.transformations import (
    derive_columns,
    remove_obvious_inconsistencies,
    select_output_columns,
)

__all__ = [
    "BuildArtifacts",
    "build_fact_orders_enriched",
    "build_payments_agg",
    "build_reviews_agg",
    "build_join_health_summary",
    "build_payment_reconciliation_summary",
    "clean_customers",
    "clean_order_items",
    "clean_orders",
    "clean_products",
    "clean_sellers",
    "clean_translation",
    "convert_datetime_columns",
    "deduplicate",
    "derive_columns",
    "remove_obvious_inconsistencies",
    "read_olist_table",
    "render_report",
    "run_build",
    "select_output_columns",
    "standardize_columns",
    "to_snake_case",
]
