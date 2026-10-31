from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src import build_analytics

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_KEY = ["order_id", "order_item_id", "product_id", "seller_id"]

EXPECTED_COLUMNS = [
    "order_id", "order_item_id", "customer_id", "customer_unique_id",
    "product_id", "seller_id", "order_status", "order_purchase_timestamp",
    "order_approved_at", "shipping_limit_date", "order_delivered_carrier_date",
    "order_delivered_customer_date", "order_estimated_delivery_date",
    "order_date", "order_year", "order_month", "purchase_cohort_month",
    "customer_first_purchase_timestamp", "cohort_order_month_number",
    "customer_order_sequence", "is_first_order", "delivery_time_days",
    "seller_dispatch_time_days", "carrier_delivery_time_days",
    "estimated_delay_days", "is_delayed", "price", "freight_value",
    "freight_to_price_ratio", "total_item_value", "payment_count",
    "total_payment_value", "max_payment_installments", "payment_type_mode",
    "review_count", "review_score_mean", "review_score_max", "review_score_min",
    "has_review_comment", "product_category_name",
    "product_category_name_english", "product_name_lenght",
    "product_description_lenght", "product_photos_qty", "product_weight_g",
    "product_length_cm", "product_height_cm", "product_width_cm",
    "customer_zip_code_prefix", "customer_city", "customer_state",
    "seller_zip_code_prefix", "seller_city", "seller_state",
    "seller_order_count", "seller_avg_delivery_days", "seller_delay_rate",
    "seller_volume_tier", "latest_review_creation_date",
    "latest_review_answer_timestamp",
]

EXPECTED_DTYPES = {
    "order_id": "object", "order_item_id": "int64", "customer_id": "object",
    "customer_unique_id": "object", "product_id": "object", "seller_id": "object",
    "order_status": "object", "order_purchase_timestamp": "datetime64[ns]",
    "order_approved_at": "datetime64[ns]", "shipping_limit_date": "datetime64[ns]",
    "order_delivered_carrier_date": "datetime64[ns]",
    "order_delivered_customer_date": "datetime64[ns]",
    "order_estimated_delivery_date": "datetime64[ns]", "order_date": "object",
    "order_year": "int32", "order_month": "int32", "purchase_cohort_month": "object",
    "customer_first_purchase_timestamp": "datetime64[ns]",
    "cohort_order_month_number": "int32", "customer_order_sequence": "Int64",
    "is_first_order": "boolean", "delivery_time_days": "float64",
    "seller_dispatch_time_days": "float64", "carrier_delivery_time_days": "float64",
    "estimated_delay_days": "float64", "is_delayed": "bool", "price": "float64",
    "freight_value": "float64", "freight_to_price_ratio": "float64",
    "total_item_value": "float64", "payment_count": "float64",
    "total_payment_value": "float64", "max_payment_installments": "float64",
    "payment_type_mode": "object", "review_count": "float64",
    "review_score_mean": "float64", "review_score_max": "float64",
    "review_score_min": "float64", "has_review_comment": "float64",
    "product_category_name": "object", "product_category_name_english": "object",
    "product_name_lenght": "float64", "product_description_lenght": "float64",
    "product_photos_qty": "float64", "product_weight_g": "float64",
    "product_length_cm": "float64", "product_height_cm": "float64",
    "product_width_cm": "float64", "customer_zip_code_prefix": "int64",
    "customer_city": "object", "customer_state": "object",
    "seller_zip_code_prefix": "int64", "seller_city": "object",
    "seller_state": "object", "seller_order_count": "Int64",
    "seller_avg_delivery_days": "float64", "seller_delay_rate": "float64",
    "seller_volume_tier": "string", "latest_review_creation_date": "datetime64[ns]",
    "latest_review_answer_timestamp": "datetime64[ns]",
}


@pytest.fixture(scope="module")
def canonical_fact(tmp_path_factory: pytest.TempPathFactory) -> pd.DataFrame:
    """Build the canonical fact in memory without writing project artifacts."""
    original_landing = build_analytics.OLIST_LANDING_DIR
    original_standardized = build_analytics.STANDARDIZED_OLIST_DIR
    build_analytics.OLIST_LANDING_DIR = ROOT / "data" / "raw" / "landing" / "olist"
    build_analytics.STANDARDIZED_OLIST_DIR = tmp_path_factory.mktemp("empty_standardized")
    try:
        return build_analytics.build_fact_orders_enriched()
    finally:
        build_analytics.OLIST_LANDING_DIR = original_landing
        build_analytics.STANDARDIZED_OLIST_DIR = original_standardized


@pytest.fixture(scope="module")
def materialized_fact_outputs(
    canonical_fact: pd.DataFrame, tmp_path_factory: pytest.TempPathFactory
) -> dict[str, Path]:
    """Persist the real canonical fact without relying on checkout artifacts."""
    output_dir = tmp_path_factory.mktemp("materialized_analytics")
    expected_paths = (
        output_dir / "fact_orders_enriched.parquet",
        output_dir / "fact_orders_enriched.csv",
        output_dir / "governance.duckdb",
    )
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(build_analytics, "ANALYTICS_DIR", output_dir)
        patch.setattr(build_analytics, "FACT_PARQUET_PATH", expected_paths[0])
        patch.setattr(build_analytics, "FACT_CSV_PATH", expected_paths[1])
        patch.setattr(build_analytics, "FACT_DUCKDB_PATH", expected_paths[2])
        written_paths = build_analytics.save_outputs(canonical_fact)
    assert written_paths == expected_paths
    assert all(path.is_file() for path in written_paths)
    return dict(zip(("parquet", "csv", "duckdb"), written_paths, strict=True))


def _control_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "price": float(df["price"].sum()),
        "freight": float(df["freight_value"].sum()),
        "item_value": float(df["total_item_value"].sum()),
        "delayed": int(df["is_delayed"].sum()),
        "delay_rate": float(df["is_delayed"].mean()),
        "first_order": int(df["is_first_order"].sum()),
    }


def _normalize_cross_format_sample(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for column, dtype in EXPECTED_DTYPES.items():
        if dtype == "datetime64[ns]" or column == "order_date":
            normalized[column] = pd.to_datetime(
                normalized[column], errors="coerce", format="mixed"
            )
        elif dtype in {"object", "string"}:
            normalized[column] = normalized[column].astype("string")
    return normalized


def test_fact_orders_enriched_schema_grain_and_dtypes(canonical_fact: pd.DataFrame) -> None:
    assert canonical_fact.shape == (112_650, 60)
    assert canonical_fact.columns.tolist() == EXPECTED_COLUMNS
    assert {column: str(dtype) for column, dtype in canonical_fact.dtypes.items()} == EXPECTED_DTYPES
    assert int(canonical_fact.duplicated(PRIMARY_KEY).sum()) == 0
    assert int(canonical_fact[PRIMARY_KEY].isna().sum().sum()) == 0


def test_fact_orders_enriched_golden_metrics(canonical_fact: pd.DataFrame) -> None:
    metrics = _control_metrics(canonical_fact)
    assert metrics["price"] == pytest.approx(13_591_643.70, abs=0.01)
    assert metrics["freight"] == pytest.approx(2_251_909.54, abs=0.01)
    assert metrics["item_value"] == pytest.approx(15_843_553.24, abs=0.01)
    assert metrics["delayed"] == 8_715
    assert metrics["delay_rate"] == pytest.approx(0.077363515, rel=1e-8)
    assert metrics["first_order"] == 109_033


def test_derived_columns_recompute_from_canonical_inputs(canonical_fact: pd.DataFrame) -> None:
    df = canonical_fact
    assert (pd.to_datetime(df["order_date"]) == df["order_purchase_timestamp"].dt.normalize()).all()
    assert (df["order_year"] == df["order_purchase_timestamp"].dt.year).all()
    assert (df["order_month"] == df["order_purchase_timestamp"].dt.month).all()
    assert (df["purchase_cohort_month"] == df["order_purchase_timestamp"].dt.to_period("M").astype(str)).all()
    expected_first = df.groupby("customer_unique_id")["order_purchase_timestamp"].transform("min")
    assert (df["customer_first_purchase_timestamp"] == expected_first).all()
    expected_cohort = ((df["order_purchase_timestamp"].dt.year - expected_first.dt.year) * 12 + df["order_purchase_timestamp"].dt.month - expected_first.dt.month)
    assert (df["cohort_order_month_number"] == expected_cohort).all()
    assert (df["is_first_order"] == (df["customer_order_sequence"] == 1)).all()

    duration_rules = {
        "delivery_time_days": ("order_delivered_customer_date", "order_purchase_timestamp"),
        "seller_dispatch_time_days": ("order_delivered_carrier_date", "order_approved_at"),
        "carrier_delivery_time_days": ("order_delivered_customer_date", "order_delivered_carrier_date"),
        "estimated_delay_days": ("order_delivered_customer_date", "order_estimated_delivery_date"),
    }
    for target, (end, start) in duration_rules.items():
        expected = (df[end] - df[start]).dt.total_seconds() / 86_400
        pd.testing.assert_series_equal(df[target], expected, check_names=False)
    expected_delayed = df["order_delivered_customer_date"].notna() & df["order_estimated_delivery_date"].notna() & (df["order_delivered_customer_date"] > df["order_estimated_delivery_date"])
    pd.testing.assert_series_equal(df["is_delayed"], expected_delayed, check_names=False)
    assert (df["total_item_value"] == df["price"] + df["freight_value"]).all()
    expected_ratio = df["freight_value"].where(df["price"] > 0).div(df["price"].where(df["price"] > 0))
    pd.testing.assert_series_equal(df["freight_to_price_ratio"], expected_ratio, check_names=False)


def test_payment_review_and_seller_aggregations_are_stable(canonical_fact: pd.DataFrame) -> None:
    df = canonical_fact
    for column in ["payment_count", "total_payment_value", "max_payment_installments", "payment_type_mode", "review_count", "review_score_mean", "review_score_max", "review_score_min", "has_review_comment"]:
        assert df.groupby("order_id", dropna=False)[column].nunique(dropna=False).max() == 1
    for column in ["seller_order_count", "seller_avg_delivery_days", "seller_delay_rate", "seller_volume_tier"]:
        assert df.groupby("seller_id", dropna=False)[column].nunique(dropna=False).max() == 1
    assert set(df["seller_volume_tier"].dropna().astype(str)) == {"long_tail", "scaled", "core", "strategic"}
    assert (df["seller_order_count"] == df.groupby("seller_id")["order_id"].transform("nunique")).all()
    assert (df["seller_volume_tier"].astype(str) == pd.cut(df["seller_order_count"], bins=[-1, 25, 100, 500, float("inf")], labels=["long_tail", "scaled", "core", "strategic"]).astype(str)).all()


@pytest.mark.parametrize("kind", ["parquet", "csv", "duckdb"])
def test_materialized_fact_outputs_logically_match_canonical(
    kind: str,
    canonical_fact: pd.DataFrame,
    materialized_fact_outputs: dict[str, Path],
) -> None:
    path = materialized_fact_outputs[kind]
    if kind == "parquet":
        actual = pd.read_parquet(path)
    elif kind == "csv":
        actual = pd.read_csv(path)
    else:
        with duckdb.connect(str(path), read_only=True) as connection:
            actual = connection.execute("SELECT * FROM fact_orders_enriched").df()
    assert actual.shape == canonical_fact.shape
    assert actual.columns.tolist() == EXPECTED_COLUMNS
    assert int(actual.duplicated(PRIMARY_KEY).sum()) == 0
    assert int(actual[PRIMARY_KEY].isna().sum().sum()) == 0
    assert _control_metrics(actual) == pytest.approx(_control_metrics(canonical_fact), rel=1e-10, abs=0.01)
    sample_keys = canonical_fact[PRIMARY_KEY].sort_values(PRIMARY_KEY).iloc[::10_000]
    expected = canonical_fact.merge(sample_keys, on=PRIMARY_KEY).sort_values(PRIMARY_KEY).reset_index(drop=True)
    observed = actual.merge(sample_keys, on=PRIMARY_KEY).sort_values(PRIMARY_KEY).reset_index(drop=True)
    assert_frame_equal(
        _normalize_cross_format_sample(observed),
        _normalize_cross_format_sample(expected),
        check_dtype=False,
        check_exact=False,
        rtol=1e-10,
        atol=1e-10,
    )
