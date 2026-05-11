from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.catalog as catalog


def test_detect_file_format_and_load_tabular_metadata_support_known_formats(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "sample.csv"
    parquet_path = tmp_path / "sample.parquet"
    pd.DataFrame({"id": [1, 2], "value": [10, 20]}).to_csv(csv_path, index=False)
    pd.DataFrame({"id": [1], "value": [10]}).to_parquet(parquet_path, index=False)

    assert catalog.detect_file_format(csv_path) == "csv"
    assert catalog.detect_file_format(parquet_path) == "parquet"
    assert catalog.load_tabular_metadata(csv_path) == (2, 2)
    assert catalog.load_tabular_metadata(parquet_path) == (1, 2)


def test_build_asset_uses_relative_path_and_metadata(tmp_path: Path) -> None:
    path = tmp_path / "asset.csv"
    pd.DataFrame({"id": [1]}).to_csv(path, index=False)

    asset = catalog.build_asset(
        path=path,
        zone="raw_landing",
        asset_type="source_table",
        description="demo",
        grain="row",
        primary_key="id",
        source_assets="source",
        publication_ready=False,
    )

    assert asset.asset_name == "asset"
    assert asset.file_format == "csv"
    assert asset.record_count == 1


def test_collect_assets_and_persist_outputs(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path
    landing_dir = base / "data" / "raw" / "landing"
    standardized_dir = base / "data" / "standardized"
    analytics_dir = base / "data" / "curated" / "analytics"
    quality_dir = base / "data" / "curated" / "quality"
    query_results_dir = base / "data" / "curated" / "query_results"
    published_dir = base / "data" / "published" / "dashboard"
    profiling_dir = base / "data" / "staging" / "profiling"
    screenshots_dir = base / "data" / "screenshots"
    sql_dir = base / "sql"
    docs_dir = base / "docs"
    catalog_dir = base / "data" / "curated" / "catalog"

    for directory in [
        landing_dir / "olist",
        standardized_dir / "olist",
        analytics_dir,
        quality_dir,
        query_results_dir,
        published_dir,
        profiling_dir,
        screenshots_dir / "query_results",
        sql_dir / "analytics",
        docs_dir,
        catalog_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"id": [1]}).to_csv(
        landing_dir / "olist" / "olist_orders_dataset.csv", index=False
    )
    pd.DataFrame({"id": [1]}).to_parquet(
        standardized_dir / "olist" / "olist_orders_dataset.parquet", index=False
    )
    pd.DataFrame({"id": [1]}).to_parquet(
        analytics_dir / "fact_orders_enriched.parquet", index=False
    )
    pd.DataFrame({"check_name": ["ok"]}).to_csv(
        quality_dir / "fact_orders_enriched_quality_checks.csv", index=False
    )
    pd.DataFrame({"query": ["q1"]}).to_csv(
        query_results_dir / "01_demo.csv", index=False
    )
    pd.DataFrame({"id": [1]}).to_parquet(
        published_dir / "fact_orders_dashboard.parquet", index=False
    )
    pd.DataFrame({"metric": [1]}).to_csv(profiling_dir / "profiling.csv", index=False)
    (screenshots_dir / "query_results" / "01_demo.png").write_bytes(b"png")
    (sql_dir / "analytics" / "01_demo.sql").write_text("select 1", encoding="utf-8")
    (docs_dir / "data_dictionary.md").write_text("# doc", encoding="utf-8")
    (docs_dir / "privacy_governance.md").write_text("# privacy", encoding="utf-8")

    monkeypatch.setattr(catalog, "LANDING_DIR", landing_dir)
    monkeypatch.setattr(catalog, "STANDARDIZED_DIR", standardized_dir)
    monkeypatch.setattr(catalog, "ANALYTICS_DIR", analytics_dir)
    monkeypatch.setattr(catalog, "QUALITY_DIR", quality_dir)
    monkeypatch.setattr(catalog, "QUERY_RESULTS_DIR", query_results_dir)
    monkeypatch.setattr(catalog, "PUBLISHED_DASHBOARD_DIR", published_dir)
    monkeypatch.setattr(catalog, "PROFILING_DIR", profiling_dir)
    monkeypatch.setattr(catalog, "SCREENSHOTS_DIR", screenshots_dir)
    monkeypatch.setattr(catalog, "SQL_DIR", sql_dir)
    monkeypatch.setattr(catalog, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(catalog, "CATALOG_DIR", catalog_dir)
    monkeypatch.setattr(
        catalog, "COLLECTION_PATH", catalog_dir / "dadosfera_collection.json"
    )
    monkeypatch.setattr(
        catalog, "ASSET_INVENTORY_PATH", catalog_dir / "collection_assets_inventory.csv"
    )
    monkeypatch.setattr(catalog, "REPORT_PATH", docs_dir / "collection_catalog.md")

    assets = catalog.collect_assets()
    collection_path, inventory_path = catalog.save_outputs(assets)
    report_path = catalog.save_report(assets)
    report = catalog.render_report(assets)

    assert len(assets) >= 8
    assert collection_path.exists()
    assert inventory_path.exists()
    assert report_path.exists()
    assert "Ativos Publicáveis da Coleção" in report
