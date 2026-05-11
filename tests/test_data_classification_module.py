from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.data_classification as data_classification


def test_build_classification_inventory_and_render_report() -> None:
    df = data_classification.build_classification_inventory()
    report = data_classification.render_report(df)

    assert not df.empty
    assert {"asset", "column", "classification", "publication_allowed"}.issubset(
        df.columns
    )
    assert "Classificação de Dados" in report
    assert "`fact_orders_dashboard`" in report


def test_save_inventory_report_and_main(tmp_path: Path, monkeypatch) -> None:
    catalog_dir = tmp_path / "catalog"
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(data_classification, "CATALOG_DIR", catalog_dir)
    monkeypatch.setattr(data_classification, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(
        data_classification,
        "CLASSIFICATION_PATH",
        catalog_dir / "data_classification_inventory.csv",
    )
    monkeypatch.setattr(
        data_classification, "REPORT_PATH", docs_dir / "data_classification.md"
    )

    df = data_classification.build_classification_inventory()
    inventory_path = data_classification.save_inventory(df)
    report_path = data_classification.save_report(df)
    data_classification.main()

    saved_df = pd.read_csv(inventory_path)
    assert inventory_path.exists()
    assert report_path.exists()
    assert len(saved_df) == len(df)
