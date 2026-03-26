# 02 Carga e Modelagem


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`

Este documento resume como os dados entram no projeto e como a camada analítica final foi construída.

## Carga e organização em camadas

Camadas implementadas:

- `data/raw/landing/olist/`
- `data/standardized/olist/`
- `data/staging/profiling/`
- `data/curated/analytics/`
- `data/published/dashboard/`

## Scripts principais da carga

- `src/ingest.py`
- `src/preprocess.py`
- `src/build_analytics.py`
- `src/publish_dashboard.py`

## Modelagem

Ativo principal:

- `fact_orders_enriched`

Granularidade:

- `1 linha por item de pedido`

Volume confirmado:

- `112.650` registros

## Camada publicada para consumo

O projeto separa explicitamente a camada analítica interna da camada publicada para consumo.

### Camada analítica interna

- ativo: `fact_orders_enriched`
- local: `data/curated/analytics/`
- uso: SQL, qualidade, governança e rastreabilidade

### Camada publicada

- ativo: `fact_orders_dashboard`
- local: `data/published/dashboard/`
- formatos:
  - `fact_orders_dashboard.parquet`
  - `fact_orders_dashboard.csv`

Uso recomendado:

- `parquet`: dashboard Streamlit local
- `csv`: upload manual na Dadosfera e evidência do ativo publicado

## Referencias detalhadas

- tabela analítica: [docs/fact_orders_enriched.md](./fact_orders_enriched.md)
- dicionario de dados: [docs/data_dictionary.md](./data_dictionary.md)
- qualidade: [docs/data_quality_report.md](./data_quality_report.md)


