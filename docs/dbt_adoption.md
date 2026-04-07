# Adoção de dbt

## Objetivo

Este documento registra a adoção de `dbt-duckdb` como camada semântica e de governança complementar ao pipeline Python.

## Princípio

`dbt` não substitui o pipeline Python atual. Ele entra para fortalecer:

- modelagem semântica sobre ativos confiáveis
- documentação automática
- testes de schema e relacionamento
- linhagem entre modelos e consumidores
- clareza da fronteira entre camada interna e camada publicada

O Python continua responsável por:

- ingestão
- construção de `fact_orders_enriched`
- publicação governada de `fact_orders_dashboard`
- monitoramento operacional
- catálogo
- exports
- app Streamlit

## Estrutura adotada

```text
dbt/
  dbt_project.yml
  profiles.yml.example
  models/
    staging/platform/
    intermediate/revenue/
    marts/core/
    marts/published/
    exposures/
  tests/
```

## Estratégia de adoção

### Fase atual

- staging tipado sobre `fact_orders_enriched` e `fact_orders_dashboard`
- fato curado e fato publicado representados em dbt sem duplicar a lógica operacional do Python
- marts semânticos publicados para KPIs executivos, categoria, estado, seller, logística e cohort
- exposures para Streamlit, Power BI e workflows analíticos
- testes de grain, completude e valores aceitos para reforçar confiança no contrato semântico

### Próximo passo recomendado

- gerar e versionar evidências visuais de `dbt docs`
- registrar as fontes Python em objetos físicos de warehouse quando o projeto sair do modo local baseado em arquivos
- ligar `dbt source freshness` a timestamps técnicos de carga quando houver metadados de ingestão no warehouse
- evoluir métricas e scorecards executivos sobre os marts já publicados

## Execução local sugerida

```bash
pip install -e .[dbt]
cd dbt
copy profiles.yml.example profiles.yml
dbt docs generate --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

Referência complementar:

- `docs/dbt_lineage.md` resume como ler o grafo semântico atual do projeto.

## Tradeoff adotado

O projeto preserva a arquitetura operacional realista. Em vez de deslocar ingestão e transformação pesada para dbt,
o repositório usa dbt onde ele agrega mais valor: semântica, testes, documentação, exposures e linhagem entre a
camada publicada e os consumidores executivos.
