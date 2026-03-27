# Operating Model

Este documento consolida o modelo operacional do projeto em uma única visão: pipeline, qualidade, governança, publicação e consumo.

## Fluxo operacional

1. Ingestão e inventário da origem
2. Padronização e profiling
3. Construção da camada analítica `fact_orders_enriched`
4. Qualidade, contratos e catálogo
5. Publicação da camada `fact_orders_dashboard`
6. Consumo por Streamlit, SQL, Power BI e evidências

## Guardrails

- qualidade automatizada em `src/quality.py`
- contratos de schema em `src/schema_contracts.py`
- catálogo local versionado em `src/catalog.py`
- publicação minimizada em `src/publish_dashboard.py`
- CI, lint e deploy versionados em `.github/workflows/`

## Responsabilidade por camada

- `raw/landing`: reprodutibilidade da fonte
- `standardized`: padronização para reuso técnico
- `staging/profiling`: análise exploratória e diagnósticos
- `curated/analytics`: camada interna de engenharia
- `published/dashboard`: camada oficial de exposição controlada

## Decisões de escopo

- o core do case está nas camadas de analytics engineering e dashboard
- artefatos bônus não mudam a operação principal do case
- integrações externas dependem de credencial e ambiente, então a automação local é a prova principal
