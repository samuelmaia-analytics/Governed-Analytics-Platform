# Arquitetura

## Visão Geral

O projeto foi reorganizado para refletir uma arquitetura simples de Data Lake em camadas, com separação clara entre entrada bruta, padronização, área intermediária de trabalho e ativos finais para consumo analítico.

Estrutura principal:

```text
data/
  raw/
    landing/
      olist/
  standardized/
    olist/
  staging/
    profiling/
  curated/
    analytics/
    quality/
    query_results/
  external/
  screenshots/
```

## Camadas

### 1. Raw / Landing

**Objetivo**

Receber os dados exatamente como chegam da fonte, sem transformações estruturais relevantes.

**Caminho**

- `data/raw/landing/olist/`

**Uso no projeto**

- fonte original dos CSVs do dataset Olist
- ponto de validação inicial em `src/ingest.py`

### 2. Standardized

**Objetivo**

Padronizar os dados de origem para um formato técnico mais consistente, com nomes de colunas normalizados e tipagem tratada para reuso nas próximas etapas.

**Caminho**

- `data/standardized/olist/`

**Uso no projeto**

- gerado por `src/preprocess.py`
- consumido preferencialmente por `src/build_analytics.py`

### 3. Staging

**Objetivo**

Armazenar artefatos intermediários, perfis exploratórios e saídas de apoio ao desenvolvimento e à validação do pipeline.

**Caminho**

- `data/staging/profiling/`

**Uso no projeto**

- resultados de profiling
- tabelas auxiliares de nulos, duplicatas e chaves candidatas

### 4. Curated / Analytics

**Objetivo**

Disponibilizar os datasets finais e confiáveis para consumo analítico, consultas SQL, validação de qualidade e dashboard.

**Caminhos**

- `data/curated/analytics/`
- `data/curated/quality/`
- `data/curated/query_results/`

**Uso no projeto**

- `fact_orders_enriched`
- resultados dos checks de qualidade
- resultados das queries SQL executadas em DuckDB

## Fluxo do Pipeline

1. `src/ingest.py`
   Valida os arquivos na camada `raw/landing` e documenta o inventário da fonte.

2. `src/preprocess.py`
   Lê os CSVs da `landing`, padroniza as tabelas e promove os datasets para `standardized`.
   Também gera artefatos exploratórios em `staging/profiling`.

3. `src/build_analytics.py`
   Lê preferencialmente da camada `standardized`, aplica joins e regras de negócio e grava a tabela final em `curated/analytics`.

4. `src/quality.py`
   Valida a tabela analítica final e salva os resultados em `curated/quality`.

5. `src/run_analytics_queries.py`
   Executa SQL sobre a camada `curated/analytics` e salva os resultados em `curated/query_results`.

6. `src/export_query_result_images.py`
   Converte os resultados tabulares das queries em PNG para documentação.

7. `streamlit_app/app.py`
   Consome `curated/analytics/fact_orders_enriched.parquet` como fonte principal do dashboard.

## Racional da Arquitetura

Esse desenho foi adotado para manter o projeto simples, mas com separação suficiente entre:

- dado de origem
- dado tecnicamente padronizado
- artefato intermediário de engenharia
- ativo final para análise e apresentação

Na prática, isso melhora a rastreabilidade, facilita a manutenção do pipeline e aproxima o projeto de um padrão real de engenharia de dados, sem introduzir complexidade desnecessária.
