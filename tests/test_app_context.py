from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.context import _build_context_from_dataframe


def test_build_context_writes_reports_only_to_injected_directory(
    tmp_path: Path,
) -> None:
    docs_dir = tmp_path / "docs"
    source_df = pd.DataFrame(
        {
            "order_id": ["order-1"],
            "customer_id": ["customer-1"],
            "price": [100.0],
            "order_purchase_timestamp": [pd.Timestamp("2018-01-01")],
        }
    )

    _build_context_from_dataframe.clear()
    context = _build_context_from_dataframe(source_df, docs_dir=docs_dir)

    assert context.df.equals(source_df)
    assert set(context.report_paths) == {
        "data_dictionary",
        "lgpd_controls",
        "data_quality_report",
        "lgpd_ripd_sample",
    }
    assert all(path.is_file() for path in context.report_paths.values())
    assert all(path.is_relative_to(docs_dir) for path in context.report_paths.values())
