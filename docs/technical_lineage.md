# Technical Lineage

Mapeamento automatizado de fluxo técnico entre fontes, transformações e ativos de saída.

| Source | Transform | Output | Layer |
| --- | --- | --- | --- |
| `data/raw/landing/olist/*.csv` | `src/preprocess.py` | `data/standardized/olist/*.parquet` | `standardized` |
| `data/standardized/olist/*.parquet` | `src/build_analytics.py` | `data/curated/analytics/fact_orders_enriched.parquet` | `curated_analytics` |
| `data/curated/analytics/fact_orders_enriched.parquet` | `src/publish_dashboard.py` | `data/published/dashboard/fact_orders_dashboard.parquet` | `published_dashboard` |
| `data/published/dashboard/fact_orders_dashboard.parquet` | `src/semantic_layer.py` | `data/published/semantic/*.parquet` | `published_semantic` |
| `data/curated/analytics/fact_orders_enriched.parquet` | `src/run_analytics_queries.py` | `data/curated/query_results/*.csv` | `curated_query_results` |
| `data/curated/query_results/*.csv` | `src/export_query_result_images.py` | `data/screenshots/query_results/*.png` | `documentation_media` |
| `data/curated/analytics/fact_orders_enriched.parquet` | `src/quality.py` | `data/curated/quality/fact_orders_enriched_quality_checks.csv` | `curated_quality` |
| `data/published/dashboard/fact_orders_dashboard.parquet` | `src/published_monitoring.py` | `data/published/monitoring/published_layer_monitoring.csv` | `published_monitoring` |
