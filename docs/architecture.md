# Arquitetura

## Visão geral

Este projeto foi estruturado como uma arquitetura simples de Data Lake em camadas, com separação clara entre:

- dado bruto de origem
- dado padronizado para reuso técnico
- artefatos intermediários de trabalho
- camada analítica interna
- camada publicada para consumo controlado

A intenção foi manter o case simples o suficiente para ser reproduzível, mas maduro o bastante para demonstrar rastreabilidade, governança e clareza de uso por camada.

## Estrutura principal das camadas

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
    genai/
    quality/
    query_results/
  published/
    dashboard/
  external/
    genai/
  screenshots/
    query_results/
```

## Leitura rápida da arquitetura

| Camada | Objetivo principal | Exemplo no projeto |
| --- | --- | --- |
| `raw/landing` | preservar a fonte original | CSVs do Olist |
| `standardized` | padronizar estrutura e tipagem | tabelas promovidas por `src/preprocess.py` |
| `staging` | guardar profiling e apoio técnico | nulos, duplicatas e chaves candidatas |
| `curated/analytics` | manter a base analítica interna | `fact_orders_enriched` |
| `curated/catalog` | materializar catálogo e inventário | manifesto JSON e inventário tabular |
| `curated/quality` | registrar checks e contratos | relatórios e resultados de qualidade |
| `curated/query_results` | persistir resultados SQL | saídas das queries em DuckDB |
| `curated/genai` | guardar artefatos do bônus de GenAI | features extraídas de texto |
| `published/dashboard` | expor camada minimizada para consumo | `fact_orders_dashboard` |
| `external/genai` | entrada auxiliar externa ao fluxo principal | amostra textual para GenAI |

## Camadas e papel no projeto

### 1. Raw / Landing

**Objetivo**

Receber os dados exatamente como chegam da fonte, sem transformação estrutural relevante.

**Caminho**

- `data/raw/landing/olist/`

**Uso no projeto**

- fonte original dos CSVs do dataset Olist
- ponto inicial de validação em `src/ingest.py`

### 2. Standardized

**Objetivo**

Promover os dados de origem para um formato mais consistente para engenharia, com colunas tratadas e persistência técnica para reuso.

**Caminho**

- `data/standardized/olist/`

**Uso no projeto**

- gerado por `src/preprocess.py`
- consumido preferencialmente por `src/build_analytics.py`

### 3. Staging

**Objetivo**

Armazenar artefatos intermediários de profiling e apoio ao desenvolvimento e à validação do pipeline.

**Caminho**

- `data/staging/profiling/`

**Uso no projeto**

- perfis de colunas
- tabelas de nulos
- duplicatas
- chaves candidatas

### 4. Curated

**Objetivo**

Concentrar os ativos já tratados e prontos para consumo técnico, auditoria, qualidade, catálogo e análise.

**Caminhos principais**

- `data/curated/analytics/`
- `data/curated/catalog/`
- `data/curated/genai/`
- `data/curated/quality/`
- `data/curated/query_results/`

**Uso no projeto**

- `fact_orders_enriched` como base analítica interna
- manifesto da coleção e inventário de ativos
- checks de qualidade e contratos simples de schema
- resultados SQL executados sobre a camada analítica
- saídas estruturadas do bônus de GenAI

### 5. Published

**Objetivo**

Separar a camada de exposição do produto analítico da camada analítica interna, aplicando minimização e pseudonimização antes do consumo pelo dashboard.

**Caminho**

- `data/published/dashboard/`

**Uso no projeto**

- `fact_orders_dashboard.parquet`
- `fact_orders_dashboard.csv`
- fonte do Streamlit
- ativo usado para publicação e evidência na Dadosfera

## Fluxo do pipeline

```text
raw/landing
  -> standardized
  -> staging/profiling
  -> curated/analytics
  -> curated/quality
  -> curated/catalog
  -> published/dashboard
  -> dashboard / SQL / BI / publicação na plataforma
```

## Etapas técnicas da solução

1. `src/ingest.py`
   Valida os arquivos de origem e documenta o inventário da fonte.

2. `src/preprocess.py`
   Padroniza as tabelas e gera os artefatos exploratórios de profiling.

3. `src/build_analytics.py`
   Constrói a `fact_orders_enriched` com granularidade de item de pedido.

4. `src/quality.py`
   Valida volume, nulos críticos, duplicidade e coerência básica da base final.

5. `src/publish_dashboard.py`
   Deriva a camada `published/dashboard` com minimização e pseudonimização.

6. `src/data_classification.py`
   Materializa a classificação de dados com foco em sensibilidade e publicação.

7. `src/schema_contracts.py`
   Aplica contratos simples de schema sobre as camadas principais.

8. `src/catalog.py`
   Materializa o manifesto da coleção e o inventário catalogável dos ativos.

9. `src/run_analytics_queries.py`
   Executa as queries SQL sobre a camada analítica.

10. `src/export_query_result_images.py`
   Converte resultados tabulares em imagens PNG para documentação.

11. `src/export_power_bi.py`
   Gera os exports do modelo complementar para Power BI.

12. `streamlit_app/app.py`
   Consome exclusivamente a camada publicada do dashboard.

13. `src/genai_feature_extraction.py`
   Materializa o bônus de extração de features em texto desestruturado.

## Decisões de arquitetura que importam na avaliação

- a camada analítica interna (`fact_orders_enriched`) foi mantida separada da camada publicada
- o dashboard não consome a camada interna completa
- a publicação na Dadosfera foi feita sobre o ativo publicado, e não sobre a base analítica completa
- catálogo, qualidade, SQL e dashboard foram tratados como partes da mesma jornada de dados

## O que está implementado versus o que é evolução

**Implementado**

- arquitetura local em camadas
- camada analítica interna
- camada publicada para dashboard
- catálogo local materializado
- publicação do ativo principal na Dadosfera com evidência visual

**Evolução futura**

- pipeline nativo recorrente na plataforma
- integração por API com catálogo/publicação
- maior absorção da arquitetura local pela Dadosfera

## Resumo executivo

Na prática, essa arquitetura permitiu organizar o case de forma defensável: o dado entra bruto, passa por padronização e validação, vira ativo analítico interno e só depois é publicado em uma camada segura para consumo. Esse desenho melhora rastreabilidade, reduz ambiguidade de uso e deixa mais clara a passagem entre dado, ativo e valor.
