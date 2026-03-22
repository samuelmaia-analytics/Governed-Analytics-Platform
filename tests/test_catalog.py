from __future__ import annotations

from src.catalog import CatalogAsset, build_collection_payload


def test_build_collection_payload_counts_publishable_assets() -> None:
    assets = [
        CatalogAsset(
            asset_name="fact_orders_enriched",
            zone="curated_analytics",
            asset_type="analytics_fact",
            relative_path="data/curated/analytics/fact_orders_enriched.parquet",
            file_format="parquet",
            description="fact",
            grain="item",
            primary_key="order_id + order_item_id + product_id + seller_id",
            source_assets="olist",
            record_count=112650,
            column_count=48,
            publication_ready=True,
        ),
        CatalogAsset(
            asset_name="olist_orders_dataset",
            zone="raw_landing",
            asset_type="source_table",
            relative_path="data/raw/landing/olist/olist_orders_dataset.csv",
            file_format="csv",
            description="raw",
            grain="source",
            primary_key="na",
            source_assets="kaggle",
            record_count=99441,
            column_count=8,
            publication_ready=False,
        ),
    ]

    payload = build_collection_payload(assets)

    assert payload["collection_id"] == "olist_analytics_case_collection"
    assert payload["publication_summary"]["total_assets"] == 2
    assert payload["publication_summary"]["publishable_assets"] == 1
