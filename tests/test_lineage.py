from __future__ import annotations

import json

from src import lineage


def test_build_lineage_edges_returns_expected_core_flow() -> None:
    edges = lineage.build_lineage_edges()
    assert edges
    assert any(edge.transform == "src/build_analytics.py" for edge in edges)
    assert any(
        edge.output == "data/published/dashboard/fact_orders_dashboard.parquet"
        for edge in edges
    )


def test_save_lineage_outputs(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(lineage, "CATALOG_DIR", tmp_path / "catalog")
    monkeypatch.setattr(lineage, "DOCS_DIR", tmp_path / "docs")
    monkeypatch.setattr(
        lineage, "LINEAGE_JSON_PATH", tmp_path / "catalog" / "technical_lineage.json"
    )
    monkeypatch.setattr(
        lineage, "LINEAGE_REPORT_PATH", tmp_path / "docs" / "technical_lineage.md"
    )
    edges = lineage.build_lineage_edges()

    json_path = lineage.save_lineage_json(edges)
    report_path = lineage.save_lineage_report(edges)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    report_text = report_path.read_text(encoding="utf-8")
    assert payload["lineage_version"] == "1.0.0"
    assert payload["edges"]
    assert "| Source | Transform | Output | Layer |" in report_text
