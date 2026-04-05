from __future__ import annotations

import pandas as pd

DEFAULT_LOCALE = "pt-BR"
SUPPORTED_LOCALES = {"pt-BR", "en-US"}
_CURRENT_LOCALE = DEFAULT_LOCALE


def set_format_locale(locale: str) -> None:
    global _CURRENT_LOCALE
    _CURRENT_LOCALE = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE


def get_format_locale() -> str:
    return _CURRENT_LOCALE


def format_date_label(value: pd.Timestamp) -> str:
    timestamp = pd.Timestamp(value)
    if get_format_locale() == "en-US":
        return timestamp.strftime("%Y-%m-%d")
    return timestamp.strftime("%d/%m/%Y")


def format_currency(value: float) -> str:
    if get_format_locale() == "en-US":
        return f"BRL {value:,.0f}"
    return f"R$ {value:,.0f}".replace(",", ".")


def format_currency_compact(value: float) -> str:
    if get_format_locale() == "en-US":
        if abs(value) >= 1_000_000:
            return f"BRL {value / 1_000_000:.1f}M"
        if abs(value) >= 1_000:
            return f"BRL {value / 1_000:.1f}K"
        return f"BRL {value:.0f}"
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"R$ {value / 1_000:.1f}K"
    return f"R$ {value:.0f}"


def format_number(value: float) -> str:
    if get_format_locale() == "en-US":
        return f"{value:,.0f}"
    return f"{value:,.0f}".replace(",", ".")


def format_pct(value: float) -> str:
    return f"{value:.1f}%"


def calc_delta(current: float, previous: float) -> str:
    if current is None or pd.isna(current):
        return "Sem base comparável"
    if previous in (0, None) or pd.isna(previous):
        return "Sem base anterior"
    delta = ((current / previous) - 1) * 100
    prefix = "+" if delta >= 0 else ""
    return f"{prefix}{delta:.1f}% vs. período anterior"


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
