from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.quality as quality


def build_quality_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "order_item_id": [1, 2, 1],
            "customer_id": ["c1", "c1", "c2"],
            "product_id": ["p1", "p2", "p3"],
            "seller_id": ["s1", "s2", "s3"],
            "order_purchase_timestamp": pd.to_datetime(
                ["2018-01-01", "2018-01-01", "2018-01-02"]
            ),
            "order_approved_at": pd.to_datetime(
                ["2018-01-01", "2018-01-01", "2018-01-03"]
            ),
            "order_delivered_customer_date": pd.to_datetime(
                ["2018-01-03", "2018-01-03", "2018-01-04"]
            ),
            "order_estimated_delivery_date": pd.to_datetime(
                ["2018-01-02", "2018-01-02", "2018-01-05"]
            ),
            "price": [100.0, 50.0, 70.0],
            "freight_value": [10.0, 5.0, 9.0],
            "review_score_mean": [4.0, 4.0, 5.0],
            "product_category_name": ["cat_a", "cat_b", "cat_c"],
            "order_year": [2018, 2018, 2018],
            "order_month": [1, 1, 1],
            "order_date": pd.to_datetime(["2018-01-01", "2018-01-01", "2018-01-02"]),
            "delivery_time_days": [2.0, 2.0, 2.0],
            "estimated_delay_days": [1.0, 1.0, -1.0],
            "is_delayed": [True, True, False],
            "total_item_value": [110.0, 55.0, 79.0],
            "customer_unique_id": ["cu1", "cu1", "cu2"],
            "customer_state": ["SP", "SP", "RJ"],
            "seller_state": ["SP", "MG", "RJ"],
            "payment_type_mode": ["credit_card", "credit_card", "boleto"],
            "total_payment_value": [165.0, 165.0, 79.0],
        }
    )


def test_validate_not_empty_and_load_fact_table(monkeypatch, tmp_path: Path) -> None:
    table_path = tmp_path / "fact.parquet"
    build_quality_dataset().to_parquet(table_path, index=False)
    monkeypatch.setattr(quality, "FACT_TABLE_PATH", table_path)

    loaded = quality.load_fact_table()

    assert len(loaded) == 3
    with pytest.raises(ValueError):
        quality.validate_not_empty(pd.DataFrame(), "demo")


def test_quality_checks_cover_schema_temporal_and_volume_failures() -> None:
    df = build_quality_dataset().drop(columns=["price"]).copy()
    df["freight_value"] = [-1.0, 5.0, 9.0]
    df["order_approved_at"] = pd.to_datetime(["2017-12-31", "2018-01-01", "2018-01-05"])
    df["order_delivered_customer_date"] = pd.to_datetime(
        ["2017-12-31", "2018-01-03", "2018-01-04"]
    )

    schema_result = quality.check_expected_schema(df)
    negatives = quality.check_negative_values(df.assign(price=[100.0, -5.0, 70.0]))
    temporal = quality.check_temporal_coherence(df.assign(price=[100.0, 50.0, 70.0]))
    volume = quality.check_record_volume(df.assign(price=[100.0, 50.0, 70.0]))

    assert schema_result.status == "FAIL"
    assert any(result.status == "FAIL" for result in negatives)
    assert any(result.status == "FAIL" for result in temporal)
    assert volume.status == "FAIL"


def test_run_quality_checks_and_render_report_include_residual_note() -> None:
    df = build_quality_dataset().copy()
    df.loc[0, "order_delivered_customer_date"] = pd.Timestamp("2017-12-31")

    results = quality.run_quality_checks(df)
    report = quality.render_quality_report(df, results)

    assert len(results) >= 10
    assert "Nota sobre a Falha Residual" in report


def test_save_quality_results_and_report_write_files(
    tmp_path: Path, monkeypatch
) -> None:
    results_path = tmp_path / "quality" / "results.csv"
    report_path = tmp_path / "docs" / "report.md"
    monkeypatch.setattr(quality, "QUALITY_DIR", results_path.parent)
    monkeypatch.setattr(quality, "DOCS_DIR", report_path.parent)
    monkeypatch.setattr(quality, "QUALITY_RESULTS_PATH", results_path)
    monkeypatch.setattr(quality, "QUALITY_REPORT_PATH", report_path)
    df = build_quality_dataset()
    results = quality.run_quality_checks(df)

    saved_results = quality.save_quality_results(results)
    saved_report = quality.save_quality_report(df, results)

    assert saved_results.exists()
    assert saved_report.exists()
    assert "Relatório de Qualidade de Dados" in saved_report.read_text(encoding="utf-8")
