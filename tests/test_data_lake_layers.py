from __future__ import annotations

from pathlib import Path

from src.data_lake_layers import load_data_lake_layers, summarize_layer_status


def test_load_data_lake_layers_reads_all_governed_layers() -> None:
    layers = load_data_lake_layers()

    layer_names = {layer.name for layer in layers}

    assert layer_names == {"bronze", "silver", "gold", "quarantine"}
    assert all(layer.governance_controls for layer in layers)
    assert all(layer.promotion_rule for layer in layers)


def test_summarize_layer_status_reports_missing_paths_against_root(tmp_path: Path) -> None:
    (tmp_path / "data" / "raw" / "landing").mkdir(parents=True)
    (tmp_path / "data" / "external").mkdir(parents=True)
    (tmp_path / "data" / "quarantine").mkdir(parents=True)

    layers = load_data_lake_layers(root_dir=tmp_path)
    status = summarize_layer_status(layers)

    bronze = next(item for item in status if item["name"] == "bronze")
    silver = next(item for item in status if item["name"] == "silver")
    quarantine = next(item for item in status if item["name"] == "quarantine")

    assert bronze["ready"] is True
    assert silver["ready"] is False
    assert quarantine["ready"] is True
    missing_path_names = {Path(path).name for path in silver["missing_paths"]}
    assert missing_path_names == {"standardized", "staging"}
