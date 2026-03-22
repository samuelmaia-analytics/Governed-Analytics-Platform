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
    catalog/
    quality/
    query_results/
  published/
    dashboard/
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
- `data/curated/catalog/`: manifesto de coleção e inventário catalogável dos ativos
- `data/curated/quality/`: resultados dos testes de qualidade
- `data/curated/query_results/`: resultados das queries SQL em CSV
- `data/published/dashboard/`: camada publicada e minimizada para consumo do Streamlit
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

5. `src/publish_dashboard.py`
   Gera a camada publicada do dashboard com minimização de dados, remoção de localização fina e pseudonimização de chaves.

6. `src/data_classification.py`
   Materializa a classificação formal dos principais campos com impacto de privacidade, risco e publicação.

7. `src/schema_contracts.py`
   Valida contratos simples de schema para as camadas `standardized`, `curated` e `published`.

8. `src/catalog.py`
   Materializa a coleção do case em JSON e CSV, com inventário de ativos e payload pronto para catalogação/publicação.

9. `src/run_analytics_queries.py`
   Executa as queries SQL em DuckDB sobre a tabela analítica e exporta os resultados em CSV.

10. `src/export_query_result_images.py`
   Converte os resultados tabulares das queries em imagens PNG legíveis para uso no markdown do case.

11. `src/export_power_bi.py`
   Gera uma fato simplificada e dimensões auxiliares para consumo externo em Power BI.

## Coleção Local vs Integração Futura

Para evitar ambiguidade na leitura do case, a distinção é a seguinte:

- **Implementado hoje**
  - uma coleção local materializada em `data/curated/catalog/dadosfera_collection.json`
  - um inventário catalogável dos ativos em `data/curated/catalog/collection_assets_inventory.csv`
  - documentação da coleção em `docs/collection_catalog.md`

- **Não implementado ainda**
  - autenticação em plataforma externa
  - publicação real em endpoint/API da Dadosfera
  - sincronização automática da coleção com um catálogo gerenciado

Em outras palavras, o projeto já entrega a estrutura e o payload da coleção em nível de prova de conceito local, mas não afirma integração nativa concluída com a plataforma.

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
- o catálogo do case em `data/curated/catalog/` permanece versionado por representar a coleção materializada
- as camadas `standardized`, `staging`, `published` e o restante de `curated` são tratadas como artefatos gerados pelo pipeline e, por isso, não precisam ser versionadas

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

### 5. Publicar a camada segura do dashboard

```bash
python src/publish_dashboard.py
```

Saídas:
- `data/published/dashboard/fact_orders_dashboard.parquet`
- `data/published/dashboard/fact_orders_dashboard.csv`
- `docs/privacy_governance.md`

### 6. Materializar a classificação de dados

```bash
python src/data_classification.py
```

Saídas:
- `data/curated/catalog/data_classification_inventory.csv`
- `docs/data_classification.md`

### 7. Validar os contratos simples de schema

```bash
python src/schema_contracts.py
```

Saídas:
- `data/curated/quality/schema_contract_results.csv`
- `docs/schema_contract_report.md`

### 8. Materializar a coleção do case

```bash
python src/catalog.py
```

Saídas:
- `data/curated/catalog/dadosfera_collection.json`
- `data/curated/catalog/collection_assets_inventory.csv`
- `docs/collection_catalog.md`

### 9. Executar testes automatizados mínimos

```bash
python -m pytest tests
```

Saída:
- suíte unitária cobrindo derivação, limpeza, qualidade e manifesto da coleção

### 10. Executar queries SQL do case

Se estiver usando a virtualenv local:

```bash
.\.venv\Scripts\python.exe src/run_analytics_queries.py
```

Saídas:
- `data/curated/query_results/*.csv`
- `data/curated/query_results/query_execution_manifest.csv`

### 11. Gerar imagens dos resultados das queries

```bash
.\.venv\Scripts\python.exe src/export_query_result_images.py
```

Saídas:
- `data/screenshots/query_results/*.png`

### 12. Gerar exportações para Power BI

```bash
python src/export_power_bi.py
```

Saída:
- `data/processed/bi_exports/`

### 13. Rodar o dashboard Streamlit

```bash
streamlit run streamlit_app/app.py
```

O app consome exclusivamente:

- `data/published/dashboard/fact_orders_dashboard.parquet`

### 14. Rodar o pipeline completo em sequência

```bash
python src/run_case_pipeline.py
```

Para listar as etapas disponíveis:

```bash
python src/run_case_pipeline.py --list-steps
```

Para executar apenas etapas específicas:

```bash
python src/run_case_pipeline.py --steps build publish classify contracts quality catalog
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
- `collection_catalog.md`: materialização da coleção/catálogo do case
- `data_dictionary.md`: dicionário de dados
- `data_classification.md`: classificação formal dos principais campos com impacto de privacidade e publicação
- `privacy_governance.md`: decisões de minimização, publicação segura e privacidade por design
- `governance_policy.md`: política de governança, retenção e accountability
- `schema_contract_report.md`: validação dos contratos simples de schema das camadas principais
- `bi_bonus.md`: orientação para o bônus em Power BI

## Privacidade, Governança e Publicação

O projeto separa explicitamente:

- `data/curated/analytics/`: camada analítica interna, usada para engenharia, SQL, qualidade e rastreabilidade
- `data/published/dashboard/`: camada publicada, minimizada e pseudonimizada para o Streamlit

Medidas implementadas:

- pseudonimização de `order_id` e `customer_unique_id` na camada publicada
- remoção de `customer_id`, `seller_id`, `product_id`, cidade e prefixos de CEP do produto analítico publicado
- preservação da camada interna para reprodutibilidade técnica e auditoria

Isso mantém o valor analítico do case sem expor granularidade desnecessária no dashboard.

## Principais Entregas

Este repositório entrega:

- estrutura profissional de projeto de dados
- camada analítica central para consulta e dashboard
- validações de qualidade com rastreabilidade
- consultas SQL executáveis em DuckDB
- resultados exportados em CSV e PNG para documentação
- material de case escrito em tom técnico e executivo
- coleção do case materializada em manifesto JSON e inventário tabular
- exportações auxiliares para BI externo
- testes automatizados mínimos para regras críticas do pipeline

## Próximos Passos

Evoluções naturais do projeto:

- ampliar o dashboard Streamlit com novas análises e exportações
- criar marts específicos por cliente, seller e categoria
- automatizar a execução completa com um orquestrador simples
- ampliar a suíte de testes para cenários relacionais, regressão analítica e UI
- integrar o manifesto da coleção a uma API real de catálogo/plataforma

## Status Atual

O projeto já possui pipeline local funcional, base analítica interna consolidada, camada publicada segura para dashboard, coleção materializada, validação de qualidade com checks de integridade e reconciliação, queries SQL executadas, imagens geradas para a documentação do case, dashboard Streamlit modularizado e exportações auxiliares para Power BI.
