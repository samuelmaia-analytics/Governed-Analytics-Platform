from __future__ import annotations

from pathlib import Path
from typing import Any


def _coerce_scalar(value: str) -> object:
    normalized = value.strip()
    if normalized.lower() == "true":
        return True
    if normalized.lower() == "false":
        return False
    return normalized


def _load_basic_yaml(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    current_section: str | None = None
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" ") and raw_line.endswith(":"):
            current_section = raw_line[:-1].strip()
            parsed[current_section] = {}
            current_list_key = None
            continue
        if current_section is None:
            continue

        line = raw_line.strip()
        section = parsed[current_section]
        if line.startswith("- ") and current_list_key:
            section[current_list_key].append(_coerce_scalar(line[2:]))
            continue
        if ":" not in line:
            continue

        key, value = [part.strip() for part in line.split(":", 1)]
        if value:
            section[key] = _coerce_scalar(value)
            current_list_key = None
        else:
            section[key] = []
            current_list_key = key

    return parsed


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-untyped]
    except ModuleNotFoundError:
        return _load_basic_yaml(text)

    return yaml.safe_load(text) or {}
