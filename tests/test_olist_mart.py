from __future__ import annotations

import logging
from collections.abc import Callable
from unittest.mock import Mock

import pandas as pd
import pytest

from src.analytics.olist.mart import build_fact_orders_enriched

SOURCE_NAMES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "product_category_name_translation.csv",
]


def _source_tables(item_count: int) -> dict[str, pd.DataFrame]:
    timestamp = pd.Timestamp("2018-01-01")
    delivered = pd.Timestamp("2018-01-03")
    estimated = pd.Timestamp("2018-01-04")
    items = pd.DataFrame(
        {
            "order_id": "o1",
            "order_item_id": pd.RangeIndex(1, item_count + 1),
            "product_id": "p1",
            "seller_id": "s1",
            "shipping_limit_date": timestamp,
            "price": 1.0,
            "freight_value": 0.5,
        },
        index=range(item_count),
    )
    return {
        "olist_orders_dataset.csv": pd.DataFrame(
            {
                "order_id": ["o1"],
                "customer_id": ["c1"],
                "order_status": ["delivered"],
                "order_purchase_timestamp": [timestamp],
                "order_approved_at": [timestamp],
                "order_delivered_carrier_date": [timestamp],
                "order_delivered_customer_date": [delivered],
                "order_estimated_delivery_date": [estimated],
            }
        ),
        "olist_order_items_dataset.csv": items,
        "olist_customers_dataset.csv": pd.DataFrame(
            {
                "customer_id": ["c1"],
                "customer_unique_id": ["cu1"],
                "customer_zip_code_prefix": [1],
                "customer_city": ["city"],
                "customer_state": ["SP"],
            }
        ),
        "olist_products_dataset.csv": pd.DataFrame(
            {"product_id": ["p1"], "product_category_name": ["category"]}
        ),
        "olist_sellers_dataset.csv": pd.DataFrame(
            {
                "seller_id": ["s1"],
                "seller_zip_code_prefix": [2],
                "seller_city": ["city"],
                "seller_state": ["RJ"],
            }
        ),
        "olist_order_payments_dataset.csv": pd.DataFrame(
            {
                "order_id": ["o1"],
                "payment_sequential": [1],
                "payment_value": [1.5 * item_count],
                "payment_installments": [1],
                "payment_type": ["credit_card"],
            }
        ),
        "olist_order_reviews_dataset.csv": pd.DataFrame(
            {
                "order_id": ["o1"],
                "review_id": ["r1"],
                "review_score": [5],
                "review_creation_date": [delivered],
                "review_answer_timestamp": [delivered],
                "review_comment_message": ["ok"],
            }
        ),
        "product_category_name_translation.csv": pd.DataFrame(
            {
                "product_category_name": ["category"],
                "product_category_name_english": ["category_en"],
            }
        ),
    }


def _loader_for(
    tables: dict[str, pd.DataFrame], calls: list[str]
) -> Callable[[str], pd.DataFrame]:
    def load(file_name: str) -> pd.DataFrame:
        calls.append(file_name)
        return tables[file_name].copy()

    return load


def test_mart_requests_each_source_once_and_validates_final_fact() -> None:
    calls: list[str] = []
    validated: list[tuple[pd.DataFrame, str]] = []
    logger = Mock(spec=logging.Logger)

    fact_table = build_fact_orders_enriched(
        read_table_fn=_loader_for(_source_tables(100_001), calls),
        validate_not_empty_fn=lambda df, name: validated.append((df, name)),
        logger=logger,
    )

    assert calls == SOURCE_NAMES
    assert len(calls) == len(set(calls)) == 8
    assert validated == [(fact_table, "fact_orders_enriched")]
    logger.info.assert_called_once_with(
        "Tabela analítica final pronta | shape=(%s, %s)", *fact_table.shape
    )


def test_mart_enforces_minimum_row_count() -> None:
    calls: list[str] = []

    with pytest.raises(
        ValueError,
        match=r"fact_orders_enriched precisa ter mais de 100\.000 registros, mas possui 1\.",
    ):
        build_fact_orders_enriched(
            read_table_fn=_loader_for(_source_tables(1), calls),
            validate_not_empty_fn=lambda _df, _name: None,
            logger=Mock(spec=logging.Logger),
        )


def test_mart_propagates_loader_failure() -> None:
    error = RuntimeError("loader failed")

    def failing_loader(_file_name: str) -> pd.DataFrame:
        raise error

    with pytest.raises(RuntimeError) as exc_info:
        build_fact_orders_enriched(
            read_table_fn=failing_loader,
            validate_not_empty_fn=lambda _df, _name: None,
            logger=Mock(spec=logging.Logger),
        )

    assert exc_info.value is error


def test_mart_propagates_validator_failure() -> None:
    calls: list[str] = []
    error = RuntimeError("validation failed")

    def failing_validator(_df: pd.DataFrame, _name: str) -> None:
        raise error

    with pytest.raises(RuntimeError) as exc_info:
        build_fact_orders_enriched(
            read_table_fn=_loader_for(_source_tables(1), calls),
            validate_not_empty_fn=failing_validator,
            logger=Mock(spec=logging.Logger),
        )

    assert exc_info.value is error
