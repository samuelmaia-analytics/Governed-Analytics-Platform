# 08 Pipelines


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento organiza a parte de pipelines do case, separando o que já foi implementado localmente, o que já foi automatizado no GitHub e o que ainda precisa ser materializado nativamente na Dadosfera.

## Objetivo

Demonstrar a capacidade de transformar, validar e publicar dados de forma reproduzivel por meio de pipeline.

## Pipeline já implementado localmente

O projeto já possui um pipeline ponta a ponta em Python, orquestrado por:

- `src/run_case_pipeline.py`

Etapas disponiveis:

- `inventory`
- `profiling`
- `build`
- `publish`
- `classify`
- `contracts`
- `quality`
- `catalog`
- `queries`
- `screenshots`
- `bi`

## Artefatos gerados pelo pipeline local

- inventário bruto
- profiling exploratorio
- `fact_orders_enriched`
- `fact_orders_dashboard`
- relatorios de qualidade
- contratos de schema
- coleção local
- resultados SQL
- screenshots das queries
- exports para Power BI

## Automação já implementada no repositório

- CI de testes em `.github/workflows/ci.yml`
- lint em `.github/workflows/lint.yml`
- promoção automática de `main` para `streamlit-prod` em `.github/workflows/deploy-streamlit.yml`
- sincronização de ativos do catálogo por API em `.github/workflows/sync-dadosfera-catalog.yml`

## Leitura de maturidade

O projeto já não depende apenas de execução manual. Há uma separação clara entre:

- pipeline analítico local, que produz os ativos centrais
- automação de engenharia no GitHub, que valida e promove artefatos
- automação de catálogo, que sincroniza ativos públicos

Isso eleva o padrão da entrega porque aproxima o case de um fluxo real de operação, sem alegar que toda a transformação já roda nativamente dentro da plataforma.

## Comando principal local

```powershell
.\.venv\Scripts\python.exe src\run_case_pipeline.py
```

## O que ainda permanece fora do escopo

Para fechar a parte especificamente nativa da plataforma, ainda falta:

- criar um pipeline real dentro da plataforma
- executar esse pipeline na plataforma
- catalogar esse pipeline
- gerar evidências visuais da execução

## Sugestao de pipeline na Dadosfera

Pipeline mínimo sugerido:

1. entrada do dataset publicado
2. etapa de tratamento ou modelagem
3. etapa de validação
4. etapa de publicação do ativo final

Sugestao de narrativa:

- ETL de modelagem e qualidade dos dados

## Evidencias que devem ser adicionadas depois

Salvar em `images/dadosfera/`:

- `06_pipeline_list.png`
- `07_pipeline_detail.png`
- `08_pipeline_run.png`
- `09_pipeline_catalog.png`

## Campos para preencher após a execução na plataforma

### Nome do pipeline na Dadosfera

- `PREENCHER`

### Objetivo do pipeline

- `PREENCHER`

### Steps utilizados

- `PREENCHER`

### Ativos de entrada

- `PREENCHER`

### Ativos de saída

- `PREENCHER`

### Link do pipeline

- `PREENCHER`

## Status atual

- pipeline local em Python: feito
- CI/CD de promoção para o branch de deploy do Streamlit: feito
- sync de catálogo via API: feito
- pipeline real na Dadosfera: pendente
- catalogação do pipeline na plataforma: pendente


