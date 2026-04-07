# Dados

Este diretório concentra os dados do projeto organizados em camadas e artefatos derivados.

## Estrutura

- `raw/landing/olist/`: arquivos CSV originais do dataset Olist
- `standardized/olist/`: tabelas padronizadas para reuso técnico
- `staging/profiling/`: saídas de profiling e EDA
- `curated/analytics/`: camada analítica interna
- `curated/quality/`: resultados de qualidade e contratos
- `curated/catalog/`: manifesto e inventário da coleção
- `curated/query_results/`: resultados materializados das queries
- `curated/genai/`: saídas do experimento de extração de features
- `published/dashboard/`: camada publicada do dashboard
- `processed/bi_exports/`: exportações para Power BI
- `screenshots/query_results/`: PNGs gerados a partir das queries
- `external/`: entradas auxiliares não transacionais

## Arquivos centrais

- camada analítica interna: `curated/analytics/fact_orders_enriched.parquet`
- camada publicada para o app: `published/dashboard/fact_orders_dashboard.parquet`
- camada publicada para upload manual na Dadosfera: `published/dashboard/fact_orders_dashboard.csv`
- slices semânticos publicados para consumo executivo: `published/semantic/*.parquet`
- export principal para BI: `processed/bi_exports/fact_sales_power_bi.csv`

## Regras de uso

- use `fact_orders_enriched` para engenharia, qualidade e SQL
- use `fact_orders_dashboard.parquet` para execução local do Streamlit
- use `published/semantic/` como contrato preferencial para KPIs, recortes executivos e reaproveitamento analítico
- use `fact_orders_dashboard.csv` para upload manual em plataforma externa
- use os arquivos de `processed/bi_exports/` no Power BI

## Observações

- o dashboard não deve consumir a camada analítica interna diretamente
- o dbt consome `curated/analytics/` e `published/dashboard/` como ativos confiáveis de entrada
- o objetivo do dbt no projeto não é refazer ingestão nem transformação pesada, e sim fortalecer a camada semântica
- os exports do Power BI usam separador `;` e encoding `utf-8-sig`
- parte das camadas derivadas pode ser recriada pelo pipeline

## Referências

- arquitetura: [../docs/architecture.md](../docs/architecture.md)
- camada dbt: [../docs/dbt_adoption.md](../docs/dbt_adoption.md)
- lineage dbt: [../docs/dbt_lineage.md](../docs/dbt_lineage.md)
- modelagem: [../docs/02_carga_e_modelagem.md](../docs/02_carga_e_modelagem.md)
- catálogo: [../docs/collection_catalog.md](../docs/collection_catalog.md)
