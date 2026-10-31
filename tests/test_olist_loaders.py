from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from src.analytics.olist.loaders import read_olist_table


def test_read_olist_table_prioritizes_standardized_and_logs_shape(
    tmp_path: Path,
) -> None:
    standardized_dir = tmp_path / "standardized"
    landing_dir = tmp_path / "landing"
    standardized_dir.mkdir()
    landing_dir.mkdir()
    pd.DataFrame({"Order ID": [1], "CustomerID": [2]}).to_parquet(
        standardized_dir / "olist_orders_dataset.parquet", index=False
    )
    (landing_dir / "olist_orders_dataset.csv").write_text(
        "Order ID,CustomerID\n3,4\n", encoding="utf-8"
    )
    load_csv = Mock(side_effect=AssertionError("landing must not be loaded"))
    logger = Mock(spec=logging.Logger)

    result = read_olist_table(
        "olist_orders_dataset.csv",
        standardized_dir=standardized_dir,
        landing_dir=landing_dir,
        load_csv_fn=load_csv,
        logger=logger,
    )

    assert result.columns.tolist() == ["order_id", "customer_id"]
    assert result.to_dict("records") == [{"order_id": 1, "customer_id": 2}]
    load_csv.assert_not_called()
    logger.info.assert_called_once_with(
        "Tabela carregada da camada standardized: %s | shape=(%s, %s)",
        "olist_orders_dataset.parquet",
        1,
        2,
    )
    logger.warning.assert_not_called()


def test_read_olist_table_falls_back_to_expected_landing_path(
    tmp_path: Path,
) -> None:
    standardized_dir = tmp_path / "standardized"
    landing_dir = tmp_path / "landing"
    landing_dir.mkdir()
    landing_path = landing_dir / "olist_orders_dataset.csv"
    landing_path.touch()
    load_csv = Mock(
        return_value=(
            pd.DataFrame({"Order ID": [3], "CustomerID": [4]}),
            "utf-8",
            [],
        )
    )
    logger = Mock(spec=logging.Logger)

    result = read_olist_table(
        "olist_orders_dataset.csv",
        standardized_dir=standardized_dir,
        landing_dir=landing_dir,
        load_csv_fn=load_csv,
        logger=logger,
    )

    assert result.columns.tolist() == ["order_id", "customer_id"]
    assert result.to_dict("records") == [{"order_id": 3, "customer_id": 4}]
    load_csv.assert_called_once_with(landing_path)
    logger.warning.assert_called_once_with(
        "Leitura realizada direto da landing para %s. Execute `python src/preprocess.py` para promover a camada standardized.",
        "olist_orders_dataset.csv",
    )
    logger.info.assert_called_once_with(
        "Tabela carregada: %s | shape=(%s, %s)",
        "olist_orders_dataset.csv",
        1,
        2,
    )


def test_read_olist_table_raises_exact_error_when_sources_are_missing(
    tmp_path: Path,
) -> None:
    standardized_dir = tmp_path / "standardized"
    landing_dir = tmp_path / "landing"
    load_csv = Mock()
    logger = Mock(spec=logging.Logger)
    standardized_path = standardized_dir / "olist_orders_dataset.parquet"
    landing_path = landing_dir / "olist_orders_dataset.csv"

    with pytest.raises(FileNotFoundError) as exc_info:
        read_olist_table(
            "olist_orders_dataset.csv",
            standardized_dir=standardized_dir,
            landing_dir=landing_dir,
            load_csv_fn=load_csv,
            logger=logger,
        )

    assert str(exc_info.value) == (
        "Arquivo não encontrado em standardized nem landing: "
        f"{standardized_path} | {landing_path}"
    )
    load_csv.assert_not_called()
    logger.info.assert_not_called()
    logger.warning.assert_not_called()
