# dbt Layer

This folder introduces dbt as a complementary modeling and documentation layer on top of the existing Python pipeline.

Recommended local setup:

```bash
pip install -e .[dbt]
cd dbt
dbt debug --profiles-dir .
dbt run --profiles-dir . --select marts.published
dbt test --profiles-dir .
```

Current adoption strategy:

- Python remains responsible for ingestion, orchestration, publication controls and operations.
- dbt is introduced first for staged SQL models, semantic marts and documentation.
- The repository keeps the current architecture intact while making semantic logic more model-driven.
