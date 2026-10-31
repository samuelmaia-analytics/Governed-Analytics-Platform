"""Construction of the canonical Olist analytical mart."""

from __future__ import annotations

import logging
from collections.abc import Callable

import pandas as pd

from src.analytics.olist.aggregations import build_payments_agg, build_reviews_agg
from src.analytics.olist.cleaning import (
    clean_customers,
    clean_order_items,
    clean_orders,
    clean_products,
    clean_sellers,
    clean_translation,
    convert_datetime_columns,
)
from src.analytics.olist.transformations import (
    derive_columns,
    remove_obvious_inconsistencies,
    select_output_columns,
)

ReadTableFn = Callable[[str], pd.DataFrame]
ValidateNotEmptyFn = Callable[[pd.DataFrame, str], None]


def build_fact_orders_enriched(
    *,
    read_table_fn: ReadTableFn,
    validate_not_empty_fn: ValidateNotEmptyFn,
    logger: logging.Logger,
) -> pd.DataFrame:
    orders = clean_orders(read_table_fn("olist_orders_dataset.csv"))
    order_items = clean_order_items(read_table_fn("olist_order_items_dataset.csv"))
    customers = clean_customers(read_table_fn("olist_customers_dataset.csv"))
    products = clean_products(read_table_fn("olist_products_dataset.csv"))
    sellers = clean_sellers(read_table_fn("olist_sellers_dataset.csv"))
    payments = build_payments_agg(
        convert_datetime_columns(read_table_fn("olist_order_payments_dataset.csv"))
    )
    reviews = build_reviews_agg(
        convert_datetime_columns(read_table_fn("olist_order_reviews_dataset.csv"))
    )
    translation = clean_translation(
        read_table_fn("product_category_name_translation.csv")
    )

    fact_table = order_items.merge(
        orders, on="order_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        customers, on="customer_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        products, on="product_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        sellers, on="seller_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        payments, on="order_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        reviews, on="order_id", how="left", validate="many_to_one"
    )
    fact_table = fact_table.merge(
        translation,
        on="product_category_name",
        how="left",
        validate="many_to_one",
    )

    fact_table = derive_columns(fact_table)
    fact_table = remove_obvious_inconsistencies(fact_table)
    fact_table = select_output_columns(fact_table)

    validate_not_empty_fn(fact_table, "fact_orders_enriched")
    if len(fact_table) <= 100_000:
        raise ValueError(
            f"fact_orders_enriched precisa ter mais de 100.000 registros, mas possui {len(fact_table)}."
        )

    logger.info("Tabela analítica final pronta | shape=(%s, %s)", *fact_table.shape)
    return fact_table
