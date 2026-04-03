from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.semantic_layer as semantic_layer


def build_semantic_source() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o2"],
            "order_item_id": [1, 1],
            "customer_unique_id": ["c1", "c1"],
            "order_year": [2018, 2018],
            "order_month": [1, 2],
            "customer_state": ["SP", "SP"],
            "seller_state": ["RJ", "RJ"],
            "seller_key": ["seller_1", "seller_1"],
            "seller_volume_tier": ["core", "core"],
            "seller_order_count": [2, 2],
            "seller_avg_delivery_days": [3.5, 3.5],
            "seller_delay_rate": [0.5, 0.5],
            "review_score_mean": [4.0, 5.0],
            "delivery_time_days": [3.0, 4.0],
            "seller_dispatch_time_days": [1.0, 1.5],
            "carrier_delivery_time_days": [2.0, 2.5],
            "payment_type_mode": ["credit_card", "boleto"],
            "freight_to_price_ratio": [0.1, 0.2],
            "product_category_name_english": ["bed_bath_table", "bed_bath_table"],
            "purchase_cohort_month": ["2018-01", "2018-01"],
            "cohort_order_month_number": [0, 1],
            "total_item_value": [100.0, 120.0],
            "is_delayed": [False, True],
        }
    )


def test_run_semantic_layer_materializes_all_slices(tmp_path: Path, monkeypatch) -> None:
    source_path = tmp_path / "fact_orders_dashboard.parquet"
    semantic_dir = tmp_path / "semantic"
    docs_dir = tmp_path / "docs"
    build_semantic_source().to_parquet(source_path, index=False)

    monkeypatch.setattr(semantic_layer, "PUBLISHED_SOURCE_PATH", source_path)
    monkeypatch.setattr(semantic_layer, "PUBLISHED_SEMANTIC_DIR", semantic_dir)
    monkeypatch.setattr(semantic_layer, "LOGISTICS_PATH", semantic_dir / "logistics_slice.parquet")
    monkeypatch.setattr(semantic_layer, "SELLER_PATH", semantic_dir / "seller_slice.parquet")
    monkeypatch.setattr(semantic_layer, "COHORT_PATH", semantic_dir / "cohort_slice.parquet")
    monkeypatch.setattr(semantic_layer, "CATEGORY_PATH", semantic_dir / "category_slice.parquet")
    monkeypatch.setattr(semantic_layer, "STATE_PATH", semantic_dir / "state_performance_slice.parquet")
    monkeypatch.setattr(semantic_layer, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(semantic_layer, "REPORT_PATH", docs_dir / "semantic_layer.md")

    artifacts = semantic_layer.run_semantic_layer()

    assert artifacts.logistics_path.exists()
    assert artifacts.seller_path.exists()
    assert artifacts.cohort_path.exists()
    assert artifacts.category_path.exists()
    assert artifacts.state_path.exists()
    assert (semantic_dir / "logistics_slice.csv").exists()
    assert (semantic_dir / "category_slice.csv").exists()
    assert (docs_dir / "semantic_layer.md").exists()
