# Data

Este diretorio concentra os dados do projeto organizados em camadas.

## Estrutura

- `raw/landing/olist/`: arquivos CSV originais
- `standardized/olist/`: tabelas padronizadas em parquet
- `staging/profiling/`: artefatos de profiling
- `curated/analytics/`: tabela analitica final
- `curated/quality/`: resultados de qualidade
- `curated/catalog/`: manifesto e inventario da colecao
- `curated/query_results/`: resultados das queries SQL
- `published/dashboard/`: camada publicada para o Streamlit
- `processed/bi_exports/`: exports para Power BI
- `screenshots/query_results/`: imagens tabulares das queries

## Arquivo mais importante para publicacao manual

Se for necessario subir o ativo principal do case em plataforma externa, utilizar:

- `published/dashboard/fact_orders_dashboard.csv`

Resumo de uso:

- `curated/analytics/fact_orders_enriched.*`: camada interna principal
- `published/dashboard/fact_orders_dashboard.parquet`: consumo do Streamlit
- `published/dashboard/fact_orders_dashboard.csv`: upload na Dadosfera
- `processed/bi_exports/*`: consumo no Power BI

## Leitura recomendada

- arquitetura: [docs/architecture.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\architecture.md)
- modelagem: [docs/02_carga_e_modelagem.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\02_carga_e_modelagem.md)
