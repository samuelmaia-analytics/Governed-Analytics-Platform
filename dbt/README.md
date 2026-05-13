# dbt — Olist Analytics

Camada de Analytics Engineering do projeto, documentando e testando as mesmas
transformações do pipeline Python em SQL declarativo com dbt + DuckDB.

## Estrutura

```
dbt/
├── dbt_project.yml          # Configuração do projeto
├── profiles.yml             # Perfil de conexão DuckDB
└── models/
    ├── staging/             # Uma model por tabela fonte (view)
    │   ├── _sources.yml     # Fontes externas (CSVs)
    │   ├── _staging.yml     # Testes e documentação
    │   └── stg_olist__*.sql
    ├── intermediate/        # Agregações pré-join (view)
    │   ├── _intermediate.yml
    │   ├── int_payments_aggregated.sql
    │   ├── int_reviews_aggregated.sql
    │   ├── int_seller_metrics.sql
    │   └── int_customer_cohort.sql
    └── marts/               # Tabelas finais materializadas
        ├── _marts.yml
        ├── fact_orders_enriched.sql    # Camada curated (interna)
        └── fact_orders_dashboard.sql  # Camada publicada (dashboard)
```

## Pré-requisitos

```bash
pip install dbt-duckdb
```

Ou com o projeto:

```bash
pip install -e ".[dev]"
```

## Como executar

```bash
cd dbt

# Definir o caminho dos CSVs de origem
export OLIST_RAW_PATH="../data/raw/landing/olist"   # Linux/macOS
set OLIST_RAW_PATH=..\data\raw\landing\olist        # Windows

# Compilar e executar todos os modelos
dbt run --profiles-dir .

# Executar apenas os marts
dbt run --profiles-dir . --select marts

# Rodar os testes
dbt test --profiles-dir .

# Ver o lineage no terminal
dbt ls --profiles-dir . --select +fact_orders_dashboard

# Gerar documentação
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## Lineage

```
olist_raw (CSVs)
    └── stg_olist__orders
    └── stg_olist__order_items
    └── stg_olist__customers
    └── stg_olist__products
    └── stg_olist__sellers
    └── stg_olist__payments       ──► int_payments_aggregated
    └── stg_olist__reviews        ──► int_reviews_aggregated
                                   ──► int_seller_metrics
                                   ──► int_customer_cohort
                                           │
                                           ▼
                               fact_orders_enriched  (curated)
                                           │
                                           ▼
                               fact_orders_dashboard (published)
```

## Convenções

| Camada         | Prefixo       | Materialização | Descrição                              |
|----------------|---------------|----------------|----------------------------------------|
| Staging        | `stg_`        | view           | Limpeza e tipagem das fontes           |
| Intermediate   | `int_`        | view           | Agregações e lógica de negócio         |
| Marts          | `fact_` / `dim_` | table       | Entregáveis para consumo analítico     |

## Relação com o pipeline Python

O pipeline Python em `src/` e o dbt são **paralelos e complementares**:

- `src/build_analytics.py` → `dbt/models/marts/fact_orders_enriched.sql`
- `src/publish_dashboard.py` → `dbt/models/marts/fact_orders_dashboard.sql`
- `src/preprocess.py` → `dbt/models/staging/stg_olist__*.sql`

O dbt adiciona: documentação versionada, testes declarativos, lineage automático
e `dbt docs` — sem substituir o pipeline operacional existente.
