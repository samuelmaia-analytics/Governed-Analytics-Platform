# Dados

Este diretório concentra os dados do projeto organizados em camadas e artefatos derivados.

## Princípios

- separar claramente camada interna (`curated`) e camada publicada (`published`);
- manter reprodutibilidade dos artefatos derivados via pipeline;
- evitar consumo direto de ativos internos por aplicações executivas.

## Estrutura

- `raw/landing/olist/`: arquivos CSV originais do dataset Olist
- `standardized/olist/`: tabelas padronizadas para reuso técnico
- `staging/profiling/`: saídas de profiling e EDA
- `curated/analytics/`: camada analítica interna
- `curated/quality/`: resultados de qualidade e contratos
- `curated/catalog/`: manifesto e inventário da coleção
- `curated/catalog/technical_lineage.json`: lineage técnico automatizado
- `curated/query_results/`: resultados materializados das queries
- `curated/genai/`: saídas do experimento de extração de features
- `published/dashboard/`: camada publicada do dashboard
- `published/monitoring/governance_scorecards.csv`: scorecards de governança por dataset
- `processed/bi_exports/`: exportações para Power BI
- `screenshots/query_results/`: PNGs gerados a partir das queries
- `external/`: entradas auxiliares não transacionais

## Arquivos centrais

- camada analítica interna: `curated/analytics/fact_orders_enriched.parquet`
- camada publicada para o app: `published/dashboard/fact_orders_dashboard.parquet`
- camada publicada para upload manual na Dadosfera: `published/dashboard/fact_orders_dashboard.csv`
- export principal para BI: `processed/bi_exports/fact_sales_power_bi.csv`

## Regras de uso

- use `fact_orders_enriched` para engenharia, qualidade e SQL
- use `fact_orders_dashboard.parquet` para execução local do Streamlit
- use `fact_orders_dashboard.csv` para upload manual em plataforma externa
- use os arquivos de `processed/bi_exports/` no Power BI

## Fluxo recomendado de consumo

1. exploração e modelagem: `raw` -> `standardized` -> `curated`
2. exposição executiva: `curated` -> `published/dashboard`
3. consumo BI externo: `published` -> `processed/bi_exports`

## Observações

- o dashboard não deve consumir a camada analítica interna diretamente
- os exports do Power BI usam separador `;` e encoding `utf-8-sig`
- parte das camadas derivadas pode ser recriada pelo pipeline

## Referências

- arquitetura: [../docs/architecture.md](../docs/architecture.md)
- modelagem: [../docs/02_carga_e_modelagem.md](../docs/02_carga_e_modelagem.md)
- catálogo: [../docs/collection_catalog.md](../docs/collection_catalog.md)
- lineage técnico: [../docs/technical_lineage.md](../docs/technical_lineage.md)
- scorecards: [../docs/governance_scorecards.md](../docs/governance_scorecards.md)
