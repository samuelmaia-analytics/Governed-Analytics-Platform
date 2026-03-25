# Projeto Olist | Case Técnico de Dados

## Visão Geral

Este repositório consolida a entrega do case técnico com foco em ciclo de vida de dados, analytics engineering, governança, consumo analítico e clareza de documentação. A solução parte do dataset Olist e o transforma em uma camada analítica confiável, auditável e reutilizável, pronta para consulta SQL, dashboard, catalogação e exploração em BI.

Em termos de avaliação, o projeto busca demonstrar quatro capacidades centrais:

- construção de pipeline analítico em camadas
- modelagem com granularidade defensável e volume acima de 100 mil registros
- preocupação real com qualidade, privacidade e rastreabilidade
- capacidade de transformar dado em ativo consumível por dashboard, catálogo e BI

A entrega principal é a tabela `fact_orders_enriched`, consolidada em:

- `data/curated/analytics/fact_orders_enriched.parquet`

Para consumo executivo, o dashboard usa exclusivamente:

- `data/published/dashboard/fact_orders_dashboard.parquet`

Para publicação externa e upload manual em plataforma, o ativo recomendado é:

- `data/published/dashboard/fact_orders_dashboard.csv`

## Resumo Executivo da Entrega

Status atual:

- GitHub publicado e atualizado
- ativo publicado na Dadosfera com evidências visuais em `images/dadosfera/`
- dashboard Streamlit operacional com fallback para `csv` no deploy
- trilha complementar de Power BI com evidências de query e dashboard

Leitura rápida para avaliador:

- ativo analítico principal: `fact_orders_enriched`
- camada publicada para consumo: `fact_orders_dashboard`
- volume final da base analítica: `112.650` linhas
- SQLs versionadas e evidenciadas
- dashboard Streamlit implementado
- ativo principal publicado na Dadosfera com evidência visual
- documentação de apoio cobrindo arquitetura, catálogo, qualidade, privacidade e apresentação

## Evidências Finais da Submissão

### Dadosfera

- Importação do dataset publicado: [images/dadosfera/01_importacao_dataset.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\01_importacao_dataset.png)
- Catalogação / documentação do ativo: [images/dadosfera/02_catalogo_metadados.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\02_catalogo_metadados.png)
- Evidência do ativo no catálogo: [images/dadosfera/03_colecao_case.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\03_colecao_case.png)
- Evidência de volume acima de 100 mil registros: [images/dadosfera/04_volume_100k.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\04_volume_100k.png)

### SQL e Evidências Analíticas

- Query principal: [sql/query_principal.sql](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\sql\query_principal.sql)
- Evidência consolidada da query: [powerbi/evidencia_query.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\evidencia_query.md)
- Print da SQL principal: [powerbi/query_principal_sql.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\query_principal_sql.png)
- Print do resultado principal: [powerbi/query_principal_resultado.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\query_principal_resultado.png)

### Dashboard e Visualizações

- Overview: [images/dashboard/01_overview.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dashboard\01_overview.png)
- Análise temporal: [images/dashboard/03_temporal.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dashboard\03_temporal.png)
- Categorias: [images/dashboard/04_categories.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dashboard\04_categories.png)
- Evidências complementares em Power BI: [powerbi/](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi)

### Apresentação

- Roteiro de apresentação: [presentation/talk_track.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\presentation\talk_track.md)
- Material complementar da apresentação: [docs/10_apresentacao_final.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\10_apresentacao_final.md)

## Mapa de Evidências

Se a leitura precisar ser feita em poucos minutos, estes são os arquivos mais importantes:

1. visão geral e posicionamento da entrega: [README.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\README.md)
2. narrativa principal do case: [docs/case_answers.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\case_answers.md)
3. carga, modelagem e volume da base: [docs/02_carga_e_modelagem.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\02_carga_e_modelagem.md)
4. catálogo e publicação do ativo: [docs/03_catalogacao.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\03_catalogacao.md)
5. perguntas analíticas e SQLs: [docs/04_analises_sql.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\04_analises_sql.md)
6. dashboard e screenshots finais: [docs/05_dashboard.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\05_dashboard.md)
7. evidência Power BI e query principal: [powerbi/evidencia_query.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\evidencia_query.md)
8. preparação da apresentação final: [docs/10_apresentacao_final.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\10_apresentacao_final.md)

## Diferença entre os Principais Ativos

### `fact_orders_enriched`

É a camada analítica interna principal do projeto.

- uso: engenharia, SQL, qualidade, auditoria e rastreabilidade
- local: `data/curated/analytics/`
- granularidade: `1 linha por item de pedido`

### `fact_orders_dashboard`

É a camada publicada do case, derivada da base analítica interna e preparada para consumo analítico.

- uso: dashboard, publicação controlada e demonstração em plataforma
- local: `data/published/dashboard/`
- formatos disponiveis:
  - `fact_orders_dashboard.parquet`: consumo local pelo Streamlit
  - `fact_orders_dashboard.csv`: upload manual na Dadosfera e compartilhamento tabular

### `fact_sales_power_bi`

É a fato simplificada do modelo estrela criado exclusivamente para BI externo.

- uso: Power BI
- local: `data/processed/bi_exports/`
- relacionamento com dimensões auxiliares

## Estrutura Principal do Case

Esta é a estrutura de entrada recomendada para leitura do case:

```text
README.md
docs/
  01_contexto.md
  02_carga_e_modelagem.md
  03_catalogacao.md
  04_analises_sql.md
  05_dashboard.md
  06_arquitetura_proposta.md
  07_bonus_genai_dataapps.md
  imagens/
sql/
  01_exploracao_inicial.sql
  02_limpeza.sql
  03_kpis.sql
  04_series_temporais.sql
  05_categorias.sql
data/
  README.md
.gitignore
```

## Como Ler o Projeto

Se você quiser seguir a mesma ordem do case, use:

0. [docs/00_planejamento.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\00_planejamento.md)
1. [docs/01_contexto.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\01_contexto.md)
2. [docs/02_carga_e_modelagem.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\02_carga_e_modelagem.md)
3. [docs/03_catalogacao.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\03_catalogacao.md)
4. [docs/04_analises_sql.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\04_analises_sql.md)
5. [docs/05_dashboard.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\05_dashboard.md)
6. [docs/06_arquitetura_proposta.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\06_arquitetura_proposta.md)
7. [docs/07_bonus_genai_dataapps.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\07_bonus_genai_dataapps.md)
8. [docs/08_pipelines.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\08_pipelines.md)
9. [docs/09_genai_llm_processar.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\09_genai_llm_processar.md)
10. [docs/10_apresentacao_final.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\10_apresentacao_final.md)

## Objetivo

O objetivo do projeto é transformar dados transacionais brutos em uma camada analítica organizada, confiável e reutilizável, capaz de:

- responder perguntas relevantes do case com SQL
- sustentar análises de receita, tempo, geografia e experiência do cliente
- servir como base para dashboard, documentação executiva e exportação para BI

## Navegação Complementar

Além da estrutura principal acima, o projeto também mantém:

- `src/`: scripts do pipeline
- `streamlit_app/`: aplicação Streamlit
- `tests/`: suíte de testes
- `presentation/`: deck e roteiro
- `powerbi/`: plano do bônus
- `images/`: evidências finais

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

Em outras palavras, o projeto já entrega a estrutura e o payload da coleção em nível de prova de conceito local. O que está comprovado na plataforma hoje é a publicação do ativo principal e sua documentação visual. O que não está sendo afirmado é integração por API ou pipeline nativo já concluídos.

Hoje, o repositório também já inclui evidências visuais da publicação do ativo na interface da Dadosfera:

- [images/dadosfera/01_importacao_dataset.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\01_importacao_dataset.png)
- [images/dadosfera/02_catalogo_metadados.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\02_catalogo_metadados.png)
- [images/dadosfera/03_colecao_case.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\03_colecao_case.png)
- [images/dadosfera/04_volume_100k.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\04_volume_100k.png)

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

Uso recomendado dos arquivos gerados:

- `fact_orders_dashboard.parquet`: app Streamlit local
- `fact_orders_dashboard.csv`: upload na Dadosfera e prova do ativo publicado

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

No deploy remoto do Streamlit, o carregamento também aceita:

- `data/published/dashboard/fact_orders_dashboard.csv`

Se a intenção for subir um ativo na Dadosfera, usar:

- `data/published/dashboard/fact_orders_dashboard.csv`

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

Para a trilha de Power BI, a evidência consolidada da query principal está em:

- [powerbi/evidencia_query.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\evidencia_query.md)

## Documentação Disponível

Arquivos principais em `docs/`:

- `case_delivery_checklist.md`: checklist da estrutura e dos entregáveis do case
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
- `03_catalogacao.md`: evidências da publicação do ativo na Dadosfera
- `10_apresentacao_final.md`: estado real da apresentação, artefatos e pendências finais

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

## Limites e Próximos Passos

Para manter honestidade técnica, estes pontos seguem como evolução e não como entrega concluída:

- pipeline nativo na Dadosfera
- integração por API para catalogação/publicação
- vídeo final da apresentação, se exigido pelo processo

Evoluções naturais da solução:

- ampliar o dashboard Streamlit com novas análises e exportações
- criar marts específicos por cliente, seller e categoria
- automatizar a execução completa com um orquestrador simples
- ampliar a suíte de testes para cenários relacionais, regressão analítica e UI
- integrar o manifesto da coleção a uma API real de catálogo/plataforma

## Status Atual

O projeto já possui pipeline local funcional, base analítica interna consolidada, camada publicada segura para dashboard, coleção materializada, validação de qualidade com checks de integridade e reconciliação, queries SQL executadas, imagens geradas para a documentação do case, dashboard Streamlit modularizado, evidências reais da publicação do ativo na Dadosfera e exportações auxiliares para Power BI.
