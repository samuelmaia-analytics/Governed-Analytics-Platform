from __future__ import annotations

from pathlib import Path

import pandas as pd

import src.preprocess as preprocess


def build_profile_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Order_ID": ["o1", "o2", "o2"],
            "Purchase_Timestamp": pd.to_datetime(["2018-01-01", "2018-01-02", "2018-01-02"]),
            "Price": [10.0, 20.0, 20.0],
            "Is_Delayed": [True, False, False],
            "Category": ["a", None, None],
        }
    )


def test_classification_profiles_and_duplicate_metrics() -> None:
    df = preprocess.standardize_columns(build_profile_frame())

    column_groups = preprocess.classify_columns(df)
    nulls_profile = preprocess.build_nulls_profile(df, "orders")
    keys_profile = preprocess.detect_possible_keys(df, column_groups["id_columns"])
    columns_profile = preprocess.build_columns_profile(df, "orders", column_groups)
    duplicate_profile = preprocess.build_duplicate_profile(df, "orders")

    assert column_groups["id_columns"] == ["order_id"]
    assert "purchase_timestamp" in column_groups["date_columns"]
    assert "price" in column_groups["numeric_columns"]
    assert "is_delayed" in column_groups["categorical_columns"]
    assert int(nulls_profile.iloc[0]["null_count"]) >= 1
    assert list(keys_profile.columns) == [
        "column_name",
        "non_null_count",
        "unique_non_null_count",
        "uniqueness_ratio",
        "null_count",
        "is_possible_key",
    ]
    assert "semantic_type" in columns_profile.columns
    assert int(duplicate_profile.iloc[0]["duplicate_rows"]) == 2


def test_save_standardized_table_and_profile_outputs(tmp_path: Path, monkeypatch) -> None:
    standardized_dir = tmp_path / "standardized"
    profiling_dir = tmp_path / "profiling"
    monkeypatch.setattr(preprocess, "STANDARDIZED_OLIST_DIR", standardized_dir)
    monkeypatch.setattr(preprocess, "PROFILING_DIR", profiling_dir)

    df = preprocess.standardize_columns(build_profile_frame())
    preprocess.save_standardized_table(df, "orders")
    preprocess.save_profile_tables(
        "orders",
        preprocess.build_columns_profile(df, "orders", preprocess.classify_columns(df)),
        preprocess.build_nulls_profile(df, "orders"),
        preprocess.detect_possible_keys(df, ["order_id"]),
        preprocess.build_duplicate_profile(df, "orders"),
    )

    assert (standardized_dir / "orders.parquet").exists()
    assert (profiling_dir / "orders_columns_profile.csv").exists()
    assert (profiling_dir / "orders_nulls_profile.csv").exists()


def test_profile_table_and_consolidated_outputs(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "orders.csv"
    build_profile_frame().to_csv(csv_path, index=False)
    monkeypatch.setattr(preprocess, "STANDARDIZED_OLIST_DIR", tmp_path / "standardized")
    monkeypatch.setattr(preprocess, "PROFILING_DIR", tmp_path / "profiling")

    profile, columns_profile, nulls_profile, keys_profile, duplicate_profile = preprocess.profile_table(
        csv_path
    )
    preprocess.save_consolidated_tables(
        [profile],
        [columns_profile],
        [nulls_profile],
        [keys_profile.assign(table_name=profile.table_name)],
        [duplicate_profile],
    )

    assert profile.table_name == "orders"
    assert profile.rows == 3
    assert (tmp_path / "profiling" / "profiling_overview.csv").exists()
    assert (tmp_path / "profiling" / "all_possible_keys.csv").exists()


def test_render_eda_summary_and_run_profiling(tmp_path: Path, monkeypatch) -> None:
    docs_dir = tmp_path / "docs"
    profiling_dir = tmp_path / "profiling"
    monkeypatch.setattr(preprocess, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(preprocess, "EDA_SUMMARY_PATH", docs_dir / "eda_summary.md")
    monkeypatch.setattr(preprocess, "PROFILING_DIR", profiling_dir)
    monkeypatch.setattr(preprocess, "STANDARDIZED_OLIST_DIR", tmp_path / "standardized")

    csv_a = tmp_path / "orders.csv"
    csv_b = tmp_path / "customers.csv"
    build_profile_frame().to_csv(csv_a, index=False)
    pd.DataFrame({"customer_id": ["c1"], "created_date": ["2018-01-01"]}).to_csv(csv_b, index=False)
    monkeypatch.setattr(preprocess, "validate_expected_files", lambda: [csv_a, csv_b])

    profiles = preprocess.run_profiling()
    report = preprocess.render_eda_summary(
        profiles,
        [preprocess.build_nulls_profile(preprocess.standardize_columns(build_profile_frame()), "orders")],
    )

    assert len(profiles) == 2
    assert "Resumo de EDA" in report
    assert (docs_dir / "eda_summary.md").exists()
