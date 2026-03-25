# Coleção e Catálogo de Ativos

Este documento materializa a coleção do case em formato versionável, pronta para publicação e catalogação.

## Objetivo

- consolidar os ativos do projeto em um inventário único e rastreável
- explicitar quais ativos estão prontos para publicação/consumo
- demonstrar uma representação concreta da coleção exigida pelo case

## Artefatos Gerados

- Manifesto JSON da coleção: `data/curated/catalog/dadosfera_collection.json`
- Inventário tabular dos ativos: `data/curated/catalog/collection_assets_inventory.csv`

## Resumo por Zona

| Zona | Total de ativos | Ativos publicáveis |
| --- | ---: | ---: |
| `analytics_sql` | 5 | 5 |
| `curated_analytics` | 1 | 0 |
| `curated_quality` | 2 | 2 |
| `curated_query_results` | 6 | 6 |
| `documentation` | 11 | 11 |
| `documentation_media` | 5 | 5 |
| `published_dashboard` | 1 | 1 |
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
| `case_answers` | `documentation` | `documentation_asset` | `docs/case_answers.md` |
| `collection_catalog` | `documentation` | `documentation_asset` | `docs/collection_catalog.md` |
| `data_classification` | `documentation` | `documentation_asset` | `docs/data_classification.md` |
| `data_classification_inventory` | `documentation` | `classification_inventory` | `data/curated/catalog/data_classification_inventory.csv` |
| `data_dictionary` | `documentation` | `documentation_asset` | `docs/data_dictionary.md` |
| `genai_bonus` | `documentation` | `documentation_asset` | `docs/genai_bonus.md` |
| `governance_policy` | `documentation` | `documentation_asset` | `docs/governance_policy.md` |
| `privacy_governance` | `documentation` | `documentation_asset` | `docs/privacy_governance.md` |
| `schema_contract_report` | `documentation` | `documentation_asset` | `docs/schema_contract_report.md` |
| `01_top_categories_by_revenue` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/01_top_categories_by_revenue.png` |
| `02_monthly_revenue_evolution` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/02_monthly_revenue_evolution.png` |
| `03_revenue_by_state` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/03_revenue_by_state.png` |
| `04_delivery_delay_by_category` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/04_delivery_delay_by_category.png` |
| `05_payment_method_distribution` | `documentation_media` | `query_screenshot` | `data/screenshots/query_results/05_payment_method_distribution.png` |
| `fact_orders_dashboard` | `published_dashboard` | `published_analytics_table` | `data/published/dashboard/fact_orders_dashboard.parquet` |

## Uso no Case

- `fact_orders_enriched` é o ativo analítico interno principal da coleção.
- `fact_orders_dashboard` é a camada publicada e minimizada usada pelo Streamlit.
- os resultados de qualidade, queries SQL e documentação derivada compõem a camada de evidência técnica do case.
- o manifesto JSON pode ser usado como payload base para publicação ou integração futura com uma API de catálogo.

## Observação

- está implementação representa uma coleção operacional em nível de projeto, adequada para prova de conceito local.
- uma integração nativa com uma plataforma externa exigiria autenticação, endpoint e contrato específicos, que não foram fornecidos no enunciado.


