from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from src.analytics.olist.outputs import (
    BuildArtifacts,
    render_report,
    save_outputs,
    save_report,
)
from src.duckdb_engine import execute_query, write_dataframe


def _report_fact() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2"],
            "total_item_value": [10.0, 15.0, 20.0],
            "total_payment_value": [25.0, 25.0, 18.0],
            "customer_unique_id": ["c1", "c1", None],
            "customer_state": ["SP", "SP", None],
            "seller_state": ["RJ", "RJ", "MG"],
            "payment_type_mode": ["credit_card", "credit_card", None],
            "product_category_name": ["cat", "cat", None],
            "product_category_name_english": ["category", "category", None],
        }
    )


def test_save_outputs_persists_all_formats_and_duckdb_table(tmp_path: Path) -> None:
    analytics_dir = tmp_path / "analytics"
    parquet_path = analytics_dir / "fact.parquet"
    csv_path = analytics_dir / "fact.csv"
    duckdb_path = analytics_dir / "fact.duckdb"
    fact_table = pd.DataFrame({"order_id": ["o1", "o2"], "value": [1.5, 2.5]})
    logger = Mock(spec=logging.Logger)

    returned = save_outputs(
        fact_table,
        analytics_dir=analytics_dir,
        parquet_path=parquet_path,
        csv_path=csv_path,
        duckdb_path=duckdb_path,
        duckdb_table="fact_orders_enriched",
        write_dataframe_fn=write_dataframe,
        logger=logger,
    )

    assert returned == (parquet_path, csv_path, duckdb_path)
    pd.testing.assert_frame_equal(pd.read_parquet(parquet_path), fact_table)
    pd.testing.assert_frame_equal(pd.read_csv(csv_path), fact_table)
    assert csv_path.read_text(encoding="utf-8").splitlines()[0] == "order_id,value"
    persisted = execute_query(
        "SELECT * FROM fact_orders_enriched ORDER BY order_id", db_path=duckdb_path
    )
    pd.testing.assert_frame_equal(persisted, fact_table)
    logger.info.assert_called_once_with(
        "Saidas salvas em %s, %s e %s::%s",
        parquet_path,
        csv_path,
        duckdb_path,
        "fact_orders_enriched",
    )


def test_save_outputs_passes_table_and_path_to_injected_writer(tmp_path: Path) -> None:
    analytics_dir = tmp_path / "analytics"
    duckdb_path = analytics_dir / "requested.duckdb"
    persisted_path = analytics_dir / "persisted.duckdb"
    fact_table = pd.DataFrame({"order_id": ["o1"]})
    writer = Mock(return_value=persisted_path)

    returned = save_outputs(
        fact_table,
        analytics_dir=analytics_dir,
        parquet_path=analytics_dir / "fact.parquet",
        csv_path=analytics_dir / "fact.csv",
        duckdb_path=duckdb_path,
        duckdb_table="fact_orders_enriched",
        write_dataframe_fn=writer,
        logger=Mock(spec=logging.Logger),
    )

    writer.assert_called_once_with(fact_table, "fact_orders_enriched", duckdb_path)
    assert returned[2] == persisted_path


def test_render_report_preserves_current_markdown_sections_and_metrics() -> None:
    report = render_report(_report_fact())

    assert report.startswith("# fact_orders_enriched\n")
    assert "- Total de registros: **3**" in report
    assert "## Regras de Negócio" in report
    assert "## Cobertura de Enriquecimento" in report
    assert "## Reconciliação Financeira em Nível de Pedido" in report
    assert "- Pedidos reconciliados: **2**" in report
    assert "## Decisão de Granularidade" in report


def test_save_report_writes_utf8_markdown_and_returns_path(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    report_path = docs_dir / "fact.md"
    fact_table = pd.DataFrame({"order_id": ["o1"]})
    content = "# Relatório\n\nInformação analítica."
    renderer = Mock(return_value=content)
    logger = Mock(spec=logging.Logger)

    returned = save_report(
        fact_table,
        docs_dir=docs_dir,
        report_path=report_path,
        render_report_fn=renderer,
        logger=logger,
    )

    assert returned == report_path
    assert report_path.read_text(encoding="utf-8") == content
    assert "Relatório".encode("utf-8") in report_path.read_bytes()
    renderer.assert_called_once_with(fact_table)
    logger.info.assert_called_once_with("Relatório salvo em %s", report_path)


def test_output_dependency_errors_are_propagated(tmp_path: Path) -> None:
    analytics_dir = tmp_path / "analytics"
    fact_table = pd.DataFrame({"order_id": ["o1"]})
    persistence_error = RuntimeError("persistence failed")
    report_error = RuntimeError("report failed")

    with pytest.raises(RuntimeError) as persistence_exc:
        save_outputs(
            fact_table,
            analytics_dir=analytics_dir,
            parquet_path=analytics_dir / "fact.parquet",
            csv_path=analytics_dir / "fact.csv",
            duckdb_path=analytics_dir / "fact.duckdb",
            duckdb_table="fact_orders_enriched",
            write_dataframe_fn=Mock(side_effect=persistence_error),
            logger=Mock(spec=logging.Logger),
        )
    assert persistence_exc.value is persistence_error

    with pytest.raises(RuntimeError) as report_exc:
        save_report(
            fact_table,
            docs_dir=tmp_path / "docs",
            report_path=tmp_path / "docs" / "fact.md",
            render_report_fn=Mock(side_effect=report_error),
            logger=Mock(spec=logging.Logger),
        )
    assert report_exc.value is report_error


def test_build_artifacts_preserves_fields_and_identity(tmp_path: Path) -> None:
    fact_table = pd.DataFrame({"order_id": ["o1"]})
    artifacts = BuildArtifacts(
        fact_table=fact_table,
        parquet_path=tmp_path / "fact.parquet",
        csv_path=tmp_path / "fact.csv",
        duckdb_path=tmp_path / "fact.duckdb",
        report_path=tmp_path / "fact.md",
    )

    assert artifacts.fact_table is fact_table
    assert list(artifacts.__dataclass_fields__) == [
        "fact_table",
        "parquet_path",
        "csv_path",
        "duckdb_path",
        "report_path",
    ]
