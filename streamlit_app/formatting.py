from __future__ import annotations

import pandas as pd


def format_currency(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def format_currency_compact(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:.1f}K"
    return f"R$ {value:.0f}"


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_pct(value: float) -> str:
    return f"{value:.1f}%"


def calc_delta(current: float, previous: float) -> str:
    if previous in (0, None) or pd.isna(previous):
        return "Sem base anterior"
    delta = ((current / previous) - 1) * 100
    prefix = "+" if delta >= 0 else ""
    return f"{prefix}{delta:.1f}% vs. período anterior"


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
