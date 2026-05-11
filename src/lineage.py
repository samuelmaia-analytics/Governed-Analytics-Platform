from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import CATALOG_DIR, DOCS_DIR
from src.ingest import configure_logging
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)
LINEAGE_JSON_PATH = CATALOG_DIR / "technical_lineage.json"
LINEAGE_REPORT_PATH = DOCS_DIR / "technical_lineage.md"


@dataclass(frozen=True)
class LineageEdge:
    source: str
    transform: str
    output: str
    layer: str


def build_lineage_edges() -> list[LineageEdge]:
    return [
        LineageEdge(
            "data/raw/landing/olist/*.csv",
            "src/preprocess.py",
            "data/standardized/olist/*.parquet",
            "standardized",
        ),
        LineageEdge(
            "data/standardized/olist/*.parquet",
            "src/build_analytics.py",
            "data/curated/analytics/fact_orders_enriched.parquet",
            "curated_analytics",
        ),
        LineageEdge(
            "data/curated/analytics/fact_orders_enriched.parquet",
            "src/publish_dashboard.py",
            "data/published/dashboard/fact_orders_dashboard.parquet",
            "published_dashboard",
        ),
        LineageEdge(
            "data/published/dashboard/fact_orders_dashboard.parquet",
            "src/semantic_layer.py",
            "data/published/semantic/*.parquet",
            "published_semantic",
        ),
        LineageEdge(
            "data/curated/analytics/fact_orders_enriched.parquet",
            "src/run_analytics_queries.py",
            "data/curated/query_results/*.csv",
            "curated_query_results",
        ),
        LineageEdge(
            "data/curated/query_results/*.csv",
            "src/export_query_result_images.py",
            "data/screenshots/query_results/*.png",
            "documentation_media",
        ),
        LineageEdge(
            "data/curated/analytics/fact_orders_enriched.parquet",
            "src/quality.py",
            "data/curated/quality/fact_orders_enriched_quality_checks.csv",
            "curated_quality",
        ),
        LineageEdge(
            "data/published/dashboard/fact_orders_dashboard.parquet",
            "src/published_monitoring.py",
            "data/published/monitoring/published_layer_monitoring.csv",
            "published_monitoring",
        ),
    ]


def save_lineage_json(edges: list[LineageEdge]) -> Path:
    ensure_directory(CATALOG_DIR)
    payload = {
        "lineage_version": "1.0.0",
        "edges": [asdict(edge) for edge in edges],
    }
    LINEAGE_JSON_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return LINEAGE_JSON_PATH


def render_lineage_report(edges: list[LineageEdge]) -> str:
    lines = [
        "# Technical Lineage",
        "",
        "Mapeamento automatizado de fluxo técnico entre fontes, transformações e ativos de saída.",
        "",
        "| Source | Transform | Output | Layer |",
        "| --- | --- | --- | --- |",
    ]
    for edge in edges:
        lines.append(
            f"| `{edge.source}` | `{edge.transform}` | `{edge.output}` | `{edge.layer}` |"
        )
    return "\n".join(lines) + "\n"


def save_lineage_report(edges: list[LineageEdge]) -> Path:
    ensure_directory(DOCS_DIR)
    LINEAGE_REPORT_PATH.write_text(render_lineage_report(edges), encoding="utf-8")
    return LINEAGE_REPORT_PATH


def main() -> None:
    configure_logging()
    edges = build_lineage_edges()
    json_path = save_lineage_json(edges)
    report_path = save_lineage_report(edges)
    LOGGER.info("Lineage técnico gerado em %s e %s", json_path, report_path)


if __name__ == "__main__":
    main()
