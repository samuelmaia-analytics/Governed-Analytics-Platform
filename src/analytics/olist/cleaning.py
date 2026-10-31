"""Column normalization and source-table cleaning for Olist analytics."""

from __future__ import annotations

import re

import pandas as pd


def to_snake_case(value: str) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", value.strip())
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_").lower()


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={column: to_snake_case(column) for column in df.columns})


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    converted = df.copy()
    for column in converted.columns:
        if "date" in column or "timestamp" in column or column.endswith("_at"):
            converted[column] = pd.to_datetime(converted[column], errors="coerce")
    return converted


def deduplicate(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset, keep="first").copy()


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    orders = convert_datetime_columns(deduplicate(orders, subset=["order_id"]))
    return orders[orders["order_id"].notna() & orders["customer_id"].notna()].copy()


def clean_order_items(order_items: pd.DataFrame) -> pd.DataFrame:
    order_items = convert_datetime_columns(deduplicate(order_items))
    order_items = order_items[
        order_items["order_id"].notna()
        & order_items["order_item_id"].notna()
        & order_items["product_id"].notna()
        & order_items["seller_id"].notna()
    ].copy()
    order_items = order_items[
        (order_items["price"].fillna(0) >= 0)
        & (order_items["freight_value"].fillna(0) >= 0)
    ].copy()
    return order_items


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    customers = deduplicate(customers, subset=["customer_id"])
    return customers[customers["customer_id"].notna()].copy()


def clean_products(products: pd.DataFrame) -> pd.DataFrame:
    products = deduplicate(products, subset=["product_id"])
    return products[products["product_id"].notna()].copy()


def clean_sellers(sellers: pd.DataFrame) -> pd.DataFrame:
    sellers = deduplicate(sellers, subset=["seller_id"])
    return sellers[sellers["seller_id"].notna()].copy()


def clean_translation(translation: pd.DataFrame) -> pd.DataFrame:
    translation = deduplicate(translation, subset=["product_category_name"])
    return translation[translation["product_category_name"].notna()].copy()
