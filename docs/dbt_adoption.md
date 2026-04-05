# Adoção de dbt

## Objetivo

Este documento registra a introdução inicial de `dbt-duckdb` no repositório como camada complementar de modelagem, testes e documentação.

## Princípio

`dbt` não substitui o pipeline Python atual. Ele entra para fortalecer:

- modularidade da modelagem SQL
- documentação automática
- testes de schema e relacionamento
- linhagem entre modelos e consumidores

O Python continua responsável por:

- ingestão
- orquestração
- governança de publicação
- monitoramento
- catálogo
- exports
- app Streamlit

## Estrutura adicionada

```text
dbt/
  dbt_project.yml
  profiles.yml.example
  models/
    staging/
    intermediate/
    marts/
    exposures/
```

## Estratégia de adoção

### Fase atual

- staging do Olist em SQL
- agregações intermediárias de pagamentos e reviews
- fato analítica inicial em dbt
- marts publicados de categoria e estado
- exposures para Streamlit e Power BI

### Próximo passo recomendado

- adicionar `dbt docs`
- evoluir testes de `accepted_values`, `not_null`, `relationships`
- migrar mais lógica semântica recorrente para marts compartilhados
- decidir se `fact_orders_enriched` continuará híbrida ou migrará integralmente para dbt

## Execução local sugerida

```bash
pip install -e .[dbt]
cd dbt
dbt run --profiles-dir .
dbt test --profiles-dir .
```

## Tradeoff adotado

O projeto preserva a arquitetura já boa e realista. A adoção de dbt foi iniciada sem reescrever todo o fluxo de uma vez, o que reduz risco e mantém a solução demonstrável para portfólio.
