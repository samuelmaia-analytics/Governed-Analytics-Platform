"""Source loading policy for Olist analytics datasets."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from src.analytics.olist.cleaning import standardize_columns

LoadCsvFn = Callable[[Path], tuple[pd.DataFrame, str, list[str]]]


def read_olist_table(
    file_name: str,
    *,
    standardized_dir: Path,
    landing_dir: Path,
    load_csv_fn: LoadCsvFn,
    logger: logging.Logger,
) -> pd.DataFrame:
    standardized_path = standardized_dir / f"{Path(file_name).stem}.parquet"
    if standardized_path.exists():
        df = pd.read_parquet(standardized_path)
        logger.info(
            "Tabela carregada da camada standardized: %s | shape=(%s, %s)",
            standardized_path.name,
            *df.shape,
        )
        return standardize_columns(df)

    landing_path = landing_dir / file_name
    if not landing_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado em standardized nem landing: {standardized_path} | {landing_path}"
        )

    df, _, _ = load_csv_fn(landing_path)
    df = standardize_columns(df)
    logger.warning(
        "Leitura realizada direto da landing para %s. Execute `python src/preprocess.py` para promover a camada standardized.",
        file_name,
    )
    logger.info("Tabela carregada: %s | shape=(%s, %s)", file_name, *df.shape)
    return df
