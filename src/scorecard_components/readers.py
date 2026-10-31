from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)
