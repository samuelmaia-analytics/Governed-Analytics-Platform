from __future__ import annotations

import pandas as pd

from src.eda import (
    correlation_matrix,
    dataset_overview,
    descriptive_statistics,
    detect_outliers_iqr,
    dtype_distribution,
    null_profile,
    top_categories,
)


def _build_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "revenue": [10.0, 12.0, 1000.0, 11.0],
            "status": ["ok", "ok", "warn", None],
            "event_date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"]),
        }
    )


def test_dataset_overview_counts_columns_by_type() -> None:
    overview = dataset_overview(_build_df())
    assert overview["total_rows"] == 4
    assert overview["total_columns"] == 3
    assert overview["numeric_columns"] == 1


def test_descriptive_statistics_returns_dataframe() -> None:
    stats = descriptive_statistics(_build_df())
    assert not stats.empty
    assert "revenue" in stats.index


def test_dtype_distribution_returns_percentage() -> None:
    dist = dtype_distribution(_build_df())
    assert {"dtype", "count", "percentage"}.issubset(set(dist.columns))


def test_top_categories_returns_categorical_summary() -> None:
    categories = top_categories(_build_df())
    assert not categories.empty
    assert "status" in categories["column_name"].values


def test_correlation_matrix_returns_numeric_correlations() -> None:
    corr = correlation_matrix(_build_df())
    assert "revenue" in corr.columns


def test_detect_outliers_iqr_flags_extreme_value() -> None:
    outliers = detect_outliers_iqr(_build_df())
    revenue_row = outliers.loc[outliers["column_name"] == "revenue"].iloc[0]
    assert int(revenue_row["outlier_count"]) >= 1


def test_null_profile_reports_null_percentage() -> None:
    profile = null_profile(_build_df())
    status_row = profile.loc[profile["column_name"] == "status"].iloc[0]
    assert float(status_row["null_pct"]) > 0.0
