# Coleção e Catálogo de Ativos

Este documento materializa a coleção do projeto em formato versionável, pronta para publicação e catalogação.

## Objetivo

- consolidar os ativos do projeto em um inventário único e rastreável
- explicitar quais ativos estão prontos para publicação/consumo
- demonstrar uma representação concreta da coleção publicada do projeto

## Artefatos Gerados

- Manifesto JSON da coleção: `data/curated/catalog/dadosfera_collection.json`
- Inventário tabular dos ativos: `data/curated/catalog/collection_assets_inventory.csv`

## Resumo por Zona

| Zona | Total de ativos | Ativos publicáveis |
| --- | ---: | ---: |
| `analytics_sql` | 5 | 5 |
| `curated_analytics` | 1 | 0 |
| `curated_ops` | 2 | 2 |
| `curated_quality` | 2 | 2 |
| `curated_query_results` | 6 | 6 |
| `documentation` | 16 | 16 |
| `documentation_media` | 5 | 5 |
| `published_dashboard` | 1 | 1 |
| `published_monitoring` | 2 | 2 |
| `published_semantic` | 5 | 5 |
| `raw_landing` | 9 | 0 |
| `staging_profiling` | 41 | 0 |
| `standardized` | 9 | 0 |

## Ativos Publicáveis da Coleção

| Ativo | Zona | Tipo | Caminho |
| --- | --- | --- | --- |
| `01_top_categories_by_revenue` | `analytics_sql` | `sql_query` | `sql/analytics/01_top_categories_by_revenue.sql` |
| `02_monthly_revenue_evolution` | `analytics_sql` | `sql_query` | `sql/analytics/02_monthly_revenue_evolution.sql` |
| `03_revenue_by_state` | `analytics_sql` | `sql_query` | `sql/analytics/03_revenue_by_state.sql` |
| `04_delivery_delay_by_category` | `analytics_sql` | `sql_query` | `sql/analytics/04_delivery_delay_by_category.sql` |
| `05_payment_method_distribution` | `analytics_sql` | `sql_query` | `sql/analytics/05_payment_method_distribution.sql` |
| `operational_job_results` | `curated_ops` | `operational_execution_log` | `data/curated/ops/operational_job_results.json` |
| `technical_lineage` | `curated_ops` | `technical_lineage` | `data/curated/catalog/technical_lineage.json` |
| `fact_orders_enriched_quality_checks` | `curated_quality` | `quality_report_table` | `data/curated/quality/fact_orders_enriched_quality_checks.csv` |
| `schema_contract_results` | `curated_quality` | `schema_contract_results` | `data/curated/quality/schema_contract_results.csv` |
| `01_top_categories_by_revenue` | `curated_query_results` | `query_result` | `data/curated/query_results/01_top_categories_by_revenue.csv` |
| `02_monthly_revenue_evolution` | `curated_query_results` | `query_result` | `data/curated/query_results/02_monthly_revenue_evolution.csv` |
| `03_revenue_by_state` | `curated_query_results` | `query_result` | `data/curated/query_results/03_revenue_by_state.csv` |
| `04_delivery_delay_by_category` | `curated_query_results` | `query_result` | `data/curated/query_results/04_delivery_delay_by_category.csv` |
| `05_payment_method_distribution` | `curated_query_results` | `query_result` | `data/curated/query_results/05_payment_method_distribution.csv` |
| `query_execution_manifest` | `curated_query_results` | `query_result` | `data/curated/query_results/query_execution_manifest.csv` |
| `about_dadosfera` | `documentation` | `documentation_asset` | `docs/about_dadosfera.md` |
| `architecture` | `documentation` | `documentation_asset` | `docs/architecture.md` |
| `collection_catalog` | `documentation` | `documentation_asset` | `docs/collection_catalog.md` |
| `data_classification` | `documentation` | `documentation_asset` | `docs/data_classification.md` |
| `data_classification_inventory` | `documentation` | `classification_inventory` | `data/curated/catalog/data_classification_inventory.csv` |
| `data_dictionary` | `documentation` | `documentation_asset` | `docs/data_dictionary.md` |
| `genai_bonus` | `documentation` | `documentation_asset` | `docs/genai_bonus.md` |
| `governance_policy` | `documentation` | `documentation_asset` | `docs/governance_policy.md` |
| `governance_scorecards` | `documentation` | `documentation_asset` | `docs/governance_scorecards.md` |
| `operational_job_report` | `documentation` | `documentation_asset` | `docs/operational_job_report.md` |
| `privacy_governance` | `documentation` | `documentation_asset` | `docs/privacy_governance.md` |
| `published_layer_monitoring` | `documentation` | `documentation_asset` | `docs/published_layer_monitoring.md` |
| `schema_contract_report` | `documentation` | `documentation_asset` | `docs/schema_contract_report.md` |
| `semantic_layer` | `documentation` | `documentation_asset` | `docs/semantic_layer.md` |
| `technical_lineage` | `documentation` | `documentation_asset` | `docs/technical_lineage.md` |
| `technical_narrative` | `documentation` | `documentation_asset` | `docs/technical_narrative.md` |
| `01_top_categories_by_revenue` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/01_top_categories_by_revenue.png` |
| `02_monthly_revenue_evolution` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/02_monthly_revenue_evolution.png` |
| `03_revenue_by_state` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/03_revenue_by_state.png` |
| `04_delivery_delay_by_category` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/04_delivery_delay_by_category.png` |
| `05_payment_method_distribution` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/05_payment_method_distribution.png` |
| `fact_orders_dashboard` | `published_dashboard` | `published_analytics_table` | `data/published/dashboard/fact_orders_dashboard.parquet` |
| `governance_scorecards` | `published_monitoring` | `governance_scorecard` | `data/published/monitoring/governance_scorecards.csv` |
| `published_layer_monitoring` | `published_monitoring` | `monitoring_result` | `data/published/monitoring/published_layer_monitoring.csv` |
| `category_slice` | `published_semantic` | `published_semantic_mart` | `data/published/semantic/category_slice.parquet` |
| `cohort_slice` | `published_semantic` | `published_semantic_mart` | `data/published/semantic/cohort_slice.parquet` |
| `logistics_slice` | `published_semantic` | `published_semantic_mart` | `data/published/semantic/logistics_slice.parquet` |
| `seller_slice` | `published_semantic` | `published_semantic_mart` | `data/published/semantic/seller_slice.parquet` |
| `state_performance_slice` | `published_semantic` | `published_semantic_mart` | `data/published/semantic/state_performance_slice.parquet` |

## Uso no Projeto

- `fact_orders_enriched` é o ativo analítico interno principal da coleção.
- `fact_orders_dashboard` é a camada publicada e minimizada usada pelo Streamlit.
- os resultados de qualidade, queries SQL e documentação derivada compõem a camada de evidência técnica do projeto.
- o manifesto JSON pode ser usado como payload base para publicação ou integração futura com uma API de catálogo.

## Observação

- esta implementação representa uma coleção operacional em nível de projeto, adequada para prova de conceito local.
- uma integração nativa com uma plataforma externa exigiria autenticação, endpoint e contrato específicos, que não foram fornecidos no enunciado.
