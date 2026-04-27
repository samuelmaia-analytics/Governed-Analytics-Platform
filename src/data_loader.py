from __future__ import annotations

from pathlib import Path

import pandas as pd

DEFAULT_SAMPLE_DATASET = Path("data/samples/sample_governance_dataset.csv")


def load_dataset(dataset_path: str | Path | None = None) -> pd.DataFrame:
    """Load a dataset from a provided path or from the project sample dataset."""
    source_path = Path(dataset_path) if dataset_path else DEFAULT_SAMPLE_DATASET
    if not source_path.exists():
        raise FileNotFoundError(f"Dataset not found: {source_path}")
    if source_path.suffix.lower() == ".parquet":
        return pd.read_parquet(source_path)
    return pd.read_csv(source_path)


def infer_dataset_name(dataset_path: str | Path | None = None) -> str:
    source_path = Path(dataset_path) if dataset_path else DEFAULT_SAMPLE_DATASET
    return source_path.stem
