# Operating Model

Este documento consolida o modelo operacional do projeto em uma única visão: pipeline, qualidade, governança, publicação e consumo.

## Princípio operacional

O projeto opera com separação explícita entre branch de desenvolvimento e branch de deploy, entre camada interna e camada publicada, e entre automação comprovada e backlog futuro. Isso evita ambiguidade sobre o que está em produção, o que está em promoção e o que ainda é evolução planejada.

## Fluxo operacional

1. Ingestão e inventário da origem
2. Padronização e profiling
3. Construção da camada analítica `fact_orders_enriched`
4. Qualidade, contratos e catálogo
5. Publicação da camada `fact_orders_dashboard`
6. Consumo por Streamlit, SQL, Power BI e evidências

## Fluxo de branches e deploy

- `main`: branch fonte de integração e branch de referência do repositório
- `streamlit-prod`: branch dedicada de deploy do Streamlit Cloud
- promoção de deploy: ocorre a partir de `main` via `.github/workflows/deploy-streamlit.yml`
- fallback operacional: em incidente de publicação, o app pode apontar explicitamente para `streamlit-prod` até normalização do fluxo principal

Leitura correta:

- merge em `main` não é o deploy final por si só
- o deploy efetivo depende da promoção bem-sucedida para `streamlit-prod`
- a validação final inclui comportamento do app publicado, não apenas CI verde

## Guardrails de release

- `CI` precisa estar verde em `main`
- `ruff` e `pytest` são reaplicados no workflow de promoção
- o branch de deploy é atualizado com `git push origin HEAD:streamlit-prod --force`
- mudanças que afetam a camada publicada exigem revalidação de artefatos, contratos e qualidade
- rollback deve ocorrer com commit explícito, sem reescrita de histórico

## Papéis operacionais por artefato

- `src/run_case_pipeline.py`: geração ponta a ponta dos ativos analíticos
- `src/publish_dashboard.py`: construção da camada publicada minimizada
- `.github/workflows/deploy-streamlit.yml`: promoção controlada de `main` para `streamlit-prod`
- `docs/release_runbook.md`: checklist mínimo antes e depois de release
- `docs/rollback_runbook.md`: resposta operacional para regressão de app ou artefato publicado

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

## Responsabilidade por ambiente

- ambiente local: geração, inspeção, testes e reprodutibilidade do case
- GitHub Actions: validação contínua e promoção da branch de deploy
- Streamlit Cloud: consumo executivo publicado
- Dadosfera/Metabase: catálogo, ativo publicado e evidências externas

## Critério de operação saudável

Uma operação saudável deste projeto exige, ao mesmo tempo:

- docs centrais alinhadas ao fluxo real
- camada `published/dashboard` consistente com contratos e quality checks
- branch `main` íntegra
- branch `streamlit-prod` atualizada pelo fluxo de promoção
- app publicado carregando a versão esperada da camada minimizada

## Decisões de escopo

- o core do case está nas camadas de analytics engineering e dashboard
- artefatos bônus não mudam a operação principal do case
- integrações externas dependem de credencial e ambiente, então a automação local é a prova principal
