from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils import ensure_directory


def append_history(snapshot: dict[str, object], *, history_path: Path) -> Path:
    ensure_directory(history_path.parent)
    row_df = pd.DataFrame([snapshot])
    if history_path.exists():
        existing = pd.read_csv(history_path)
        row_df = pd.concat([existing, row_df], ignore_index=True)
    row_df.to_csv(history_path, index=False)
    return history_path
