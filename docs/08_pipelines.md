# 08 Pipelines


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/governed-analytics-platform`
- Dashboard Streamlit: `https://governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento organiza a parte de pipelines do projeto, separando o que já foi implementado localmente, o que já foi automatizado no GitHub e o que ainda precisa ser materializado nativamente na plataforma.

## Objetivo

Demonstrar a capacidade de transformar, validar e publicar dados de forma reproduzivel por meio de pipeline.

## Pipeline já implementado localmente

O projeto já possui um pipeline ponta a ponta em Python, orquestrado por:

- `src/run_platform_pipeline.py`

Etapas disponiveis:

- `inventory`
- `profiling`
- `build`
- `publish`
- `semantic`
- `classify`
- `contracts`
- `quality`
- `monitor`
- `catalog`
- `queries`
- `screenshots`
- `bi`

## Artefatos gerados pelo pipeline local

- inventário bruto
- profiling exploratorio
- `fact_orders_enriched`
- `fact_orders_dashboard`
- marts semanticos de logistica, seller e cohort
- relatorio operacional do job
- relatorio de freshness e qualidade da camada published
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
- job agendado da camada published em `.github/workflows/operate-published-layer.yml`

## Leitura de maturidade

O projeto já não depende apenas de execução manual. Há uma separação clara entre:

- pipeline analítico local, que produz os ativos centrais
- automação de engenharia no GitHub, que valida e promove artefatos
- automação de catálogo, que sincroniza ativos públicos

Isso eleva o padrão da solução porque aproxima o projeto de um fluxo real de operação, sem alegar que toda a transformação já roda nativamente dentro da plataforma.

## Leitura correta do item

O escopo pedia um pipeline na plataforma, mas a leitura tecnicamente rigorosa deste repositório é a seguinte:

- o pipeline analítico principal foi implementado e validado em `Python`
- o ativo final `fact_orders_dashboard` foi efetivamente publicado na Dadosfera
- o consumo do ativo na plataforma foi comprovado por catálogo, visualização e evidências
- a execução nativa completa da transformação dentro do módulo de pipelines da Dadosfera ainda não foi comprovada como fluxo final deste tenant

Essa distinção é intencional. O projeto evita marcar o item como concluído de forma inflada quando o que existe com evidência é publicação, catálogo, visualização e preparação operacional para pipeline nativo.

## Comando principal local

```powershell
.\.venv\Scripts\python.exe src\run_platform_pipeline.py
```

## O que ainda permanece fora do escopo

Para fechar a parte especificamente nativa da plataforma, ainda falta:

- criar um pipeline real dentro da plataforma
- executar esse pipeline na plataforma
- catalogar esse pipeline
- gerar evidências visuais da execução

## O que foi preparado para reduzir esse gap

Mesmo sem evidência final de um pipeline nativo executado na interface da plataforma, o repositório já foi preparado para a próxima etapa:

- operador de pipelines via API em `src/dadosfera_pipeline_ops.py`
- suporte a credencial não interativa por token no operador e no sync de catálogo
- comando `deploy` idempotente para reaproveitar pipeline existente e executar por API
- runbook operacional em `docs/dadosfera_native_pipeline_runbook.md`
- template versionado para tentativa real em `contracts/dadosfera/pipelines/fact_orders_dashboard_s3_parquet_pipeline.json`

Com isso, a lacuna remanescente deixa de ser modelagem conceitual e passa a ser dependência de origem compatível, configuração real no tenant e evidência de run bem-sucedido.

## Desenho recomendado para pipeline nativo na Dadosfera

Pipeline mínimo sugerido:

1. entrada do dataset publicado
2. etapa de tratamento ou modelagem
3. etapa de validação
4. etapa de publicação do ativo final

Narrativa recomendada:

- ETL de modelagem e qualidade dos dados

## Evidências esperadas se a implementação nativa ocorrer

Salvar em `images/dadosfera/`:

- `06_pipeline_list.png`
- `07_pipeline_detail.png`
- `08_pipeline_run.png`
- `09_pipeline_catalog.png`

## Critério de aceite para evoluir este item

Este tópico só deve ser promovido de backlog para implementação concluída quando houver, no mínimo:

- nome real do pipeline na plataforma
- link navegável do pipeline
- evidência visual da execução
- evidência visual da catalogação
- descrição dos ativos de entrada e saída baseada em implementação real, não em plano

Até lá, a leitura correta é:

- existe pipeline local ponta a ponta em Python
- existe automação de engenharia e promoção de deploy no GitHub
- não existe pipeline nativo da plataforma comprovado por evidência

## Backlog explícito de evolução

Se houver aprofundamento futuro na plataforma, os campos que precisam ser preenchidos com evidência real são:

- nome do pipeline na Dadosfera
- objetivo operacional do pipeline
- steps efetivamente utilizados
- ativos de entrada
- ativos de saída
- link do pipeline

## Status atual

- pipeline local em Python: feito
- CI/CD de promoção para o branch de deploy do Streamlit: feito
- sync de catálogo via API: feito
- monitoramento recorrente da camada published: feito
- jobs agendados com observabilidade de falha: feito
- expansão semântica de logística, seller e cohort: feita
- preparação operacional para pipeline nativo via API: feita
- pipeline real na Dadosfera: pendente
- catalogação do pipeline na plataforma: pendente



