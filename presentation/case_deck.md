# Case Deck

## Slide 1 - Capa

- Projeto: `SAMUEL_MAIA_DDF_TECH_032026`
- Tema: Analytics Engineering e Data Product com dados do Olist
- Objetivo: transformar dados brutos de e-commerce em camada analítica confiável, consultável e pronta para consumo executivo

## Slide 2 - Problema

- O dataset Olist possui múltiplas tabelas transacionais e exige integração entre pedidos, itens, clientes, produtos, sellers, pagamentos e reviews
- O desafio do case é sair do dado bruto e chegar a uma base analítica que responda perguntas de negócio com rastreabilidade
- Além da análise, a entrega precisava contemplar documentação, SQL, dashboard e visão de publicação/catalogação

## Slide 3 - Arquitetura

- Camadas implementadas:
  - `data/raw/landing/olist/`
  - `data/standardized/olist/`
  - `data/staging/profiling/`
  - `data/curated/analytics/`
  - `data/curated/quality/`
  - `data/curated/catalog/`
  - `data/published/dashboard/`
- Referência visual: [docs/architecture.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\architecture.md)
- Sugestão de fala:
  - começar explicando que o projeto separa dado bruto, dado padronizado, dado analítico interno e dado publicado
  - enfatizar que o dashboard consome apenas a camada publicada

## Slide 4 - Pipeline

- `src/ingest.py`: valida arquivos de origem
- `src/preprocess.py`: padroniza e gera profiling
- `src/build_analytics.py`: constrói a `fact_orders_enriched`
- `src/quality.py`: executa checks de qualidade
- `src/publish_dashboard.py`: gera camada segura para consumo
- `src/run_case_pipeline.py`: orquestra tudo ponta a ponta

## Slide 5 - Tabela Analítica Principal

- Ativo central: [data/curated/analytics/fact_orders_enriched.parquet](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\curated\analytics\fact_orders_enriched.parquet)
- Granularidade: `1 linha por item de pedido`
- Volume final: `112.650` linhas
- Colunas: `48`
- Uso: SQL, qualidade, documentação e derivação da camada publicada
- Mensagem principal:
  - a modelagem foi feita para preservar detalhe operacional e ainda permitir leitura executiva

## Slide 6 - Governança e Publicação

- Camada interna: `fact_orders_enriched`
- Camada publicada: [data/published/dashboard/fact_orders_dashboard.parquet](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\published\dashboard\fact_orders_dashboard.parquet)
- Medidas aplicadas:
  - pseudonimização de `order_id` e `customer_unique_id`
  - remoção de identificadores e quase-identificadores desnecessários
- Referência: [docs/privacy_governance.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\privacy_governance.md)

## Slide 7 - SQL e Insights

- Queries salvas em [sql/analytics/](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\sql\analytics)
- Resultados exportados em [data/curated/query_results/](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\curated\query_results)
- Evidências tabulares em [data/screenshots/query_results/](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\screenshots\query_results)
- Principais leituras:
  - concentração comercial em poucas categorias e estados
  - aceleração temporal com pressão operacional em meses de pico
  - alta dependência de `credit_card`
- Sugestão visual:
  - colocar um mosaico com 2 ou 3 screenshots de `data/screenshots/query_results/`

## Slide 8 - Dashboard

- App em [streamlit_app/app.py](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\streamlit_app\app.py)
- Fonte exclusiva: `data/published/dashboard/fact_orders_dashboard.parquet`
- Blocos principais:
  - KPIs
  - tendência temporal
  - categorias
  - geografia
  - operação
  - insights executivos
- Screenshots finais já disponíveis:
  - [images/dashboard/01_overview.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dashboard\01_overview.png)
  - [images/dashboard/02_kpis.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dashboard\02_kpis.png)
  - [images/dashboard/03_temporal.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dashboard\03_temporal.png)
  - [images/dashboard/04_categories.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dashboard\04_categories.png)
  - [images/dashboard/05_geography.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dashboard\05_geography.png)
- Sugestão de uso no slide:
  - imagem principal: `01_overview.png`
  - imagens de apoio: `03_temporal.png`, `04_categories.png` e `05_geography.png`
- Mensagem principal:
  - o dashboard nao e apenas visual; ele consome uma camada publicada e minimizada, coerente com a governanca do projeto

## Slide 9 - Catálogo e Dadosfera

- Existe catálogo local em:
  - [data/curated/catalog/dadosfera_collection.json](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\curated\catalog\dadosfera_collection.json)
  - [data/curated/catalog/collection_assets_inventory.csv](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\curated\catalog\collection_assets_inventory.csv)
- Status honesto:
  - estrutura de publicação e metadados está pronta localmente
  - a materialização real na plataforma Dadosfera ainda depende de execução manual e captura de evidência
- Recomendação para fala:
  - dizer explicitamente que o repositorio ja entrega o payload e o inventario
  - nao vender como integracao real concluida enquanto os prints da plataforma nao existirem
- Quando os prints forem capturados, inserir:
  - `images/dadosfera/01_asset_list.png`
  - `images/dadosfera/02_asset_preview.png`
  - `images/dadosfera/04_catalog.png`
- Referencia operacional: [docs/dadosfera_capture_runbook.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\dadosfera_capture_runbook.md)

## Slide 10 - Testes e Robustez

- Suíte em [tests/](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\tests)
- Validações cobrindo:
  - build analítico
  - catálogo
  - filtros do dashboard
  - publicação segura
  - qualidade
  - runner do pipeline
  - contratos de schema

## Slide 11 - Bônus de BI

- Exports preparados em [data/processed/bi_exports/](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\processed\bi_exports)
- Status honesto:
  - base pronta para Power BI
  - dashboard Power BI ainda precisa ser materializado, se o bônus for usado
- Referencia operacional: [powerbi/delivery_plan.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\delivery_plan.md)

## Slide 12 - Próximos Passos

- publicar dataset e catálogo real na Dadosfera
- capturar evidências finais da plataforma
- integrar os screenshots finais do Streamlit ao deck final
- opcional: materializar o bônus em Power BI
- fechar commit final e push no GitHub
