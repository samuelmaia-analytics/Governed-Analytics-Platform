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
    catalog/
    quality/
    query_results/
  published/
    dashboard/
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

Disponibilizar os datasets finais e confiáveis para consumo analítico interno, consultas SQL e validação de qualidade.

**Caminhos**

- `data/curated/analytics/`
- `data/curated/catalog/`
- `data/curated/quality/`
- `data/curated/query_results/`

**Uso no projeto**

- `fact_orders_enriched`
- manifesto da coleção do case e inventário de ativos catalogáveis
- resultados dos checks de qualidade
- resultados das queries SQL executadas em DuckDB

### 5. Published / Dashboard

**Objetivo**

Separar a camada de exposição do produto analítico da camada analítica interna, aplicando minimização e pseudonimização antes do consumo pelo dashboard.

**Caminho**

- `data/published/dashboard/`

**Uso no projeto**

- `fact_orders_dashboard.parquet`
- fonte exclusiva do Streamlit
- redução de identificadores, cidades e prefixos de CEP na camada publicada

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

5. `src/publish_dashboard.py`
   Deriva a camada `published/dashboard` a partir de `fact_orders_enriched`, aplicando pseudonimização e minimização para exposição analítica.

6. `src/data_classification.py`
   Materializa o inventário de classificação de dados, com foco em sensibilidade, risco e ação de publicação.

7. `src/schema_contracts.py`
   Valida contratos simples de schema sobre as camadas `standardized`, `curated` e `published`, reforçando consistência estrutural.

8. `src/catalog.py`
   Materializa a coleção do case em arquivos versionáveis, com manifesto JSON e inventário tabular dos ativos publicados e intermediários.

9. `src/run_analytics_queries.py`
   Executa SQL sobre a camada `curated/analytics` e salva os resultados em `curated/query_results`.

10. `src/export_query_result_images.py`
   Converte os resultados tabulares das queries em PNG para documentação.

11. `streamlit_app/app.py`
   Consome `published/dashboard/fact_orders_dashboard.parquet` como fonte principal do dashboard.

## Racional da Arquitetura

Esse desenho foi adotado para manter o projeto simples, mas com separação suficiente entre:

- dado de origem
- dado tecnicamente padronizado
- artefato intermediário de engenharia
- ativo final interno para análise
- ativo publicado para apresentação controlada

Na prática, isso melhora a rastreabilidade, facilita a manutenção do pipeline, reforça governança por camada e adiciona privacidade por design sem enfraquecer o valor analítico do case.
