from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.config import ROOT_DIR

DEFAULT_LAYER_CONFIG_PATH = ROOT_DIR / "config" / "data_lake_layers.yml"


@dataclass(frozen=True)
class DataLakeLayer:
    name: str
    label: str
    paths: tuple[Path, ...]
    purpose: str
    allowed_formats: tuple[str, ...]
    governance_controls: tuple[str, ...]
    promotion_rule: str
    owner_role: str
    sensitivity_default: str

    def existing_paths(self) -> tuple[Path, ...]:
        return tuple(path for path in self.paths if path.exists())

    def missing_paths(self) -> tuple[Path, ...]:
        return tuple(path for path in self.paths if not path.exists())

    @property
    def is_ready(self) -> bool:
        return not self.missing_paths()


def _as_tuple(raw_value: Any) -> tuple[str, ...]:
    if raw_value is None:
        return ()
    if isinstance(raw_value, list):
        return tuple(str(item) for item in raw_value)
    return (str(raw_value),)


def load_data_lake_layers(
    config_path: Path = DEFAULT_LAYER_CONFIG_PATH,
    *,
    root_dir: Path = ROOT_DIR,
) -> tuple[DataLakeLayer, ...]:
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    raw_layers = config.get("layers", {})
    layers: list[DataLakeLayer] = []
    for layer_name, layer_config in raw_layers.items():
        relative_paths = _as_tuple(layer_config.get("paths"))
        layers.append(
            DataLakeLayer(
                name=str(layer_name),
                label=str(layer_config["label"]),
                paths=tuple(root_dir / path for path in relative_paths),
                purpose=str(layer_config["purpose"]),
                allowed_formats=_as_tuple(layer_config.get("allowed_formats")),
                governance_controls=_as_tuple(
                    layer_config.get("governance_controls")
                ),
                promotion_rule=str(layer_config["promotion_rule"]),
                owner_role=str(layer_config["owner_role"]),
                sensitivity_default=str(layer_config["sensitivity_default"]),
            )
        )
    return tuple(layers)


def summarize_layer_status(
    layers: tuple[DataLakeLayer, ...] | None = None,
) -> list[dict[str, object]]:
    inspected_layers = layers if layers is not None else load_data_lake_layers()
    return [
        {
            "layer": layer.label,
            "name": layer.name,
            "ready": layer.is_ready,
            "path_count": len(layer.paths),
            "existing_path_count": len(layer.existing_paths()),
            "missing_paths": [str(path) for path in layer.missing_paths()],
            "owner_role": layer.owner_role,
            "sensitivity_default": layer.sensitivity_default,
            "governance_controls": list(layer.governance_controls),
        }
        for layer in inspected_layers
    ]
