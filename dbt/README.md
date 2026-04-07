# dbt Layer

This folder positions dbt as the semantic, documentation, testing, and lineage layer on top of the existing Python pipeline.

Recommended local setup:

```bash
pip install -e .[dbt]
cd dbt
copy profiles.yml.example profiles.yml
dbt debug --profiles-dir .
dbt parse --profiles-dir .
dbt run --profiles-dir . --select marts.published
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
```

Current adoption strategy:

- Python remains responsible for ingestion, standardization, analytical fact construction, publication controls, monitoring, and operations.
- dbt starts from trusted Python outputs in `data/curated/analytics/` and `data/published/dashboard/`.
- dbt owns semantic marts, schema tests, lineage, exposures, and business-facing documentation for executive consumption.

Current model layout:

```text
models/
  staging/platform/
  intermediate/revenue/
  marts/core/
  marts/published/
  exposures/
tests/
```

Architectural intent:

- `fct_orders_enriched` remains Python-owned and is surfaced in dbt for lineage and governance.
- `fct_orders_dashboard` is the published boundary for executive consumption.
- downstream marts such as `mart_executive_kpis`, `mart_category_performance`, `mart_state_performance`,
  `mart_logistics_performance`, `mart_seller_performance`, and `mart_customer_cohorts` provide reusable semantic outputs.

Validation status in this repository:

- `dbt debug --profiles-dir .` validated the local DuckDB connection
- `dbt run --profiles-dir .` materialized the current graph successfully
- `dbt test --profiles-dir .` passed on the implemented models and marts

Repository-specific references:

- lineage reading guide: `../docs/dbt_lineage.md`
- adoption rationale: `../docs/dbt_adoption.md`
