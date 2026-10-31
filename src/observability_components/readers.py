from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_governance_history(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    history_df = pd.read_csv(path)
    if "execution_timestamp" in history_df.columns:
        history_df = history_df.sort_values("execution_timestamp")
    return history_df
