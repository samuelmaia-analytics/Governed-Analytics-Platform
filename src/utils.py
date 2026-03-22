from pathlib import Path

import pandas as pd


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def write_csv(df: pd.DataFrame, path: Path, **kwargs) -> None:
    ensure_directory(path.parent)
    df.to_csv(path, index=False, **kwargs)
