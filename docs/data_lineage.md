# Data Lineage

Este documento descreve a linhagem logica do Governed Analytics Platform, da
fonte Olist ate os pontos de consumo governados.

## Fluxo De Linhagem

```text
Fontes Olist / CSV
↓
Bronze / Raw
↓
Silver / Cleaned
↓
Gold / Governed Marts
↓
Publication Gate
↓
Streamlit / Dashboards / APIs
```

## Descricao Das Etapas

- **Fontes Olist / CSV**: arquivos publicos usados como entrada do projeto.
- **Bronze / Raw**: preservacao de dados brutos e landing zone local.
- **Silver / Cleaned**: dados limpos, padronizados e perfilados.
- **Gold / Governed Marts**: marts, datasets publicados, scorecards e artefatos governados.
- **Publication Gate**: decisao formal de publicacao com base em qualidade, LGPD e issues criticas.
- **Streamlit / Dashboards / APIs**: consumo executivo e tecnico sobre dados governados.

## Tabela De Linhagem

| source_dataset | bronze_layer | silver_layer | gold_layer | consumption_layer | owner | refresh_frequency | lgpd_risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `olist_orders_dataset.csv` | `data/bronze/` and `data/raw/landing/olist/` | `data/silver/` and `data/standardized/` | `data/gold/`, `data/curated/`, `data/published/` | Streamlit Executive Overview, API governance status | Analytics Engineering | On demand / simulated scheduled run | Medium |
| `olist_order_items_dataset.csv` | `data/bronze/` and `data/raw/landing/olist/` | `data/silver/` and `data/standardized/` | `data/gold/`, `data/curated/`, `data/published/` | Revenue Analytics, Power BI exports | Analytics Engineering | On demand / simulated scheduled run | Low |
| `olist_customers_dataset.csv` | `data/bronze/` and `data/raw/landing/olist/` | `data/silver/` and `data/standardized/` | Governed aggregates only | Streamlit published layer, semantic slices | Data Governance | On demand / simulated scheduled run | High |
| `olist_products_dataset.csv` | `data/bronze/` and `data/raw/landing/olist/` | `data/silver/` and `data/standardized/` | `data/curated/genai/`, `data/published/semantic/` | GenAI Insights, Data Catalog | Analytics Engineering | On demand / simulated scheduled run | Low |
| `product_category_name_translation.csv` | `data/bronze/` and `data/raw/landing/olist/` | `data/silver/` and `data/standardized/` | `data/curated/`, `data/published/semantic/` | Category analytics and semantic views | Analytics Engineering | On demand / simulated scheduled run | Low |

## Controles De Governanca Na Linhagem

- Classificacao LGPD antes de publicacao.
- Checks de qualidade antes de promover datasets.
- Contratos de schema e regras de negocio versionados.
- Publication Gate para registrar `Approved`, `Needs Review` ou `Blocked`.
- Consumo executivo preferencialmente a partir de `data/published/`.
