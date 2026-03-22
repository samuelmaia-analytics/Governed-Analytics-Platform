# Projeto Olist | Case Técnico de Dados

## Visão Geral

Este repositório contém uma solução local de engenharia e análise de dados construída sobre o dataset Olist. O projeto foi estruturado para cobrir o fluxo completo do case: ingestão, profiling, modelagem analítica, validação de qualidade, consultas SQL e preparação de insumos para documentação, dashboard e bônus de BI.

A entrega principal é a tabela `fact_orders_enriched`, que consolida informações de pedidos, itens, produtos, clientes, sellers, pagamentos e reviews em uma base analítica única, pronta para exploração em SQL, markdown e Streamlit.

## Objetivo

O objetivo do projeto é transformar dados transacionais brutos em uma camada analítica organizada, confiável e reutilizável, capaz de:

- responder perguntas relevantes do case com SQL
- sustentar análises de receita, tempo, geografia e experiência do cliente
- servir como base para dashboard, documentação executiva e exportação para BI

## Estrutura do Projeto

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
    query_results/
  processed/
    bi_exports/

notebooks/
sql/
  exploratory/
  analytics/
src/
streamlit_app/
docs/
tests/
```

Pastas principais:

- `data/raw/landing/olist/`: arquivos CSV originais do dataset
- `data/standardized/olist/`: tabelas padronizadas para consumo interno do pipeline
- `data/staging/profiling/`: saídas da análise exploratória inicial
- `data/curated/analytics/`: tabela analítica final
- `data/curated/quality/`: resultados dos testes de qualidade
- `data/curated/query_results/`: resultados das queries SQL em CSV
- `data/screenshots/query_results/`: imagens PNG das tabelas geradas para o markdown
- `data/processed/bi_exports/`: exportações auxiliares para Power BI
- `sql/analytics/`: consultas do case em DuckDB
- `src/`: scripts Python do pipeline
- `docs/`: documentação técnica e executiva

## Arquitetura do Pipeline

O pipeline foi organizado em etapas modulares:

1. `src/ingest.py`
   Valida os CSVs do dataset Olist, carrega os arquivos e gera o inventário dos dados brutos.

2. `src/preprocess.py`
   Executa a análise exploratória inicial, com perfil de colunas, nulos, duplicatas e possíveis chaves.

3. `src/build_analytics.py`
   Monta a tabela `fact_orders_enriched`, preservando granularidade por item de pedido e criando colunas derivadas para análise.

4. `src/quality.py`
   Valida schema, nulos críticos, duplicidade, coerência temporal e volume mínimo da tabela final.

5. `src/run_analytics_queries.py`
   Executa as queries SQL em DuckDB sobre a tabela analítica e exporta os resultados em CSV.

6. `src/export_query_result_images.py`
   Converte os resultados tabulares das queries em imagens PNG legíveis para uso no markdown do case.

7. `src/export_power_bi.py`
   Gera uma fato simplificada e dimensões auxiliares para consumo externo em Power BI.

## Tabela Analítica Principal

Arquivos principais:

- `data/curated/analytics/fact_orders_enriched.parquet`
- `data/curated/analytics/fact_orders_enriched.csv`

Características da tabela:

- granularidade: `1 linha por item de pedido`
- volume final: `112.650` registros
- colunas derivadas:
  - `order_year`
  - `order_month`
  - `order_date`
  - `delivery_time_days`
  - `estimated_delay_days`
  - `is_delayed`
  - `total_item_value`

Essa modelagem foi escolhida para equilibrar detalhamento operacional e capacidade analítica.

## Requisitos

Dependências principais:

- `pandas`
- `numpy`
- `streamlit`
- `plotly`
- `matplotlib`
- `seaborn`
- `duckdb`
- `pyarrow`
- `openpyxl`
- `python-dotenv`
- `jinja2`

Instalação:

```bash
pip install -r requirements.txt
```

## Política de Versionamento de Dados

Para manter o repositório aderente a um formato de entrega de case técnico, foi adotada a seguinte estratégia:

- os arquivos raw do case em `data/raw/landing/olist/` permanecem versionados
- os screenshots usados na documentação permanecem versionados em `data/screenshots/query_results/`
- as camadas `standardized`, `staging` e `curated` são tratadas como artefatos gerados pelo pipeline e, por isso, não precisam ser versionadas

Essa decisão preserva reprodutibilidade e leitura do case sem poluir o repositório com saídas que podem ser recriadas localmente.

## Como Executar

### 1. Gerar o inventário dos dados brutos

```bash
python src/ingest.py
```

Saída:
- `docs/raw_data_inventory.md`

### 2. Rodar a análise exploratória inicial

```bash
python src/preprocess.py
```

Saídas:
- `docs/eda_summary.md`
- `data/standardized/olist/`
- `data/staging/profiling/`

### 3. Construir a tabela analítica principal

```bash
python src/build_analytics.py
```

Saídas:
- `data/curated/analytics/fact_orders_enriched.parquet`
- `data/curated/analytics/fact_orders_enriched.csv`
- `docs/fact_orders_enriched.md`

### 4. Validar a qualidade da tabela final

```bash
python src/quality.py
```

Saídas:
- `docs/data_quality_report.md`
- `data/curated/quality/fact_orders_enriched_quality_checks.csv`

### 5. Executar queries SQL do case

Se estiver usando a virtualenv local:

```bash
.\.venv\Scripts\python.exe src/run_analytics_queries.py
```

Saídas:
- `data/curated/query_results/*.csv`
- `data/curated/query_results/query_execution_manifest.csv`

### 6. Gerar imagens dos resultados das queries

```bash
.\.venv\Scripts\python.exe src/export_query_result_images.py
```

Saídas:
- `data/screenshots/query_results/*.png`

### 7. Gerar exportações para Power BI

```bash
python src/export_power_bi.py
```

Saída:
- `data/processed/bi_exports/`

### 8. Rodar o dashboard Streamlit

```bash
streamlit run streamlit_app/app.py
```

## Consultas SQL do Case

As principais perguntas analíticas foram organizadas em `sql/analytics/`:

- `01_top_categories_by_revenue.sql`
- `02_monthly_revenue_evolution.sql`
- `03_revenue_by_state.sql`
- `04_delivery_delay_by_category.sql`
- `05_payment_method_distribution.sql`

Essas queries respondem perguntas sobre receita, evolução temporal, distribuição geográfica, atraso logístico e meios de pagamento.

## Documentação Disponível

Arquivos principais em `docs/`:

- `case_answers.md`: narrativa principal do case
- `raw_data_inventory.md`: inventário dos dados brutos
- `eda_summary.md`: resumo exploratório inicial
- `fact_orders_enriched.md`: documentação da tabela analítica
- `data_quality_report.md`: relatório de qualidade da base final
- `architecture.md`: visão geral da arquitetura
- `data_dictionary.md`: dicionário de dados
- `bi_bonus.md`: orientação para o bônus em Power BI

## Principais Entregas

Este repositório entrega:

- estrutura profissional de projeto de dados
- camada analítica central para consulta e dashboard
- validações de qualidade com rastreabilidade
- consultas SQL executáveis em DuckDB
- resultados exportados em CSV e PNG para documentação
- material de case escrito em tom técnico e executivo
- exportações auxiliares para BI externo

## Próximos Passos

Evoluções naturais do projeto:

- ampliar o dashboard Streamlit com novas análises e exportações
- criar marts específicos por cliente, seller e categoria
- incluir testes automatizados para o pipeline
- automatizar a execução completa com um orquestrador simples
- expandir a camada de visualização além das tabelas estáticas

## Status Atual

O projeto já possui pipeline local funcional, base analítica consolidada, validação de qualidade, queries SQL executadas, imagens geradas para a documentação do case e exportações auxiliares para Power BI.
