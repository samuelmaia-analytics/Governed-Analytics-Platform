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
6. Expansão semântica e monitoramento recorrente da camada publicada
7. Consumo por Streamlit, SQL, Power BI e evidências

## Fluxo de branches e deploy

- `develop`: branch fonte do ambiente `dev`
- `release`: branch fonte do ambiente `stage`
- `main`: branch fonte do ambiente `prod` e branch de referência do repositório
- `streamlit-dev`, `streamlit-stage`, `streamlit-prod`: branches dedicadas de deploy do Streamlit Cloud
- promoção de deploy: ocorre via `.github/workflows/deploy-streamlit.yml`, com resolução explícita do plano de promoção por ambiente
- fallback operacional: em incidente de publicação, o ambiente afetado pode permanecer no branch de deploy anterior até normalização do fluxo

Leitura correta:

- merge em uma branch fonte não é o deploy final por si só
- o deploy efetivo depende da promoção bem-sucedida para `streamlit-dev`, `streamlit-stage` ou `streamlit-prod`
- a validação final inclui comportamento do app publicado no ambiente alvo, não apenas CI verde

## Guardrails de release

- `CI` e `Lint` executam em `develop`, `release` e `main`
- `Policy Check` valida o contrato versionado de governança e os gatilhos reais dos workflows
- `CI` valida também `python src/governance_validation.py`
- `ruff` e `pytest` são reaplicados no workflow de promoção
- o branch de deploy é atualizado com `git push origin HEAD:<deployment_branch> --force`
- mudanças que afetam a camada publicada exigem revalidação de artefatos, contratos e qualidade
- rollback deve ocorrer com commit explícito, sem reescrita de histórico

## Papéis operacionais por artefato

- `src/run_case_pipeline.py`: geração ponta a ponta dos ativos analíticos
- `src/publish_dashboard.py`: construção da camada publicada minimizada
- `src/semantic_layer.py`: marts publicados para logística, seller e cohort
- `src/published_monitoring.py`: freshness e qualidade recorrente da camada publicada
- `.github/workflows/operate-published-layer.yml`: job agendado com artefatos operacionais e falha observável
- `.github/workflows/deploy-streamlit.yml`: promoção controlada de `develop`, `release` ou `main` para o branch de deploy do ambiente correspondente
- `.github/workflows/policy-check.yml`: valida aderência entre workflows e contrato de governança
- `contracts/governance/release_governance.json`: contrato canônico de branches, ambientes e workflows
- `src/governance_validation.py`: validação do contrato de release
- `src/workflow_policy_validation.py`: validação dos workflows contra o contrato
- `docs/release_runbook.md`: checklist mínimo antes e depois de release
- `docs/rollback_runbook.md`: resposta operacional para regressão de app ou artefato publicado

## Guardrails

- qualidade automatizada em `src/quality.py`
- contratos de schema em `src/schema_contracts.py`
- catálogo local versionado em `src/catalog.py`
- publicação minimizada em `src/publish_dashboard.py`
- CI, lint e deploy versionados em `.github/workflows/`
- autenticação não interativa na API da Dadosfera por `DADOSFERA_ACCESS_TOKEN` ou `DADOSFERA_API_TOKEN`

## Responsabilidade por camada

- `raw/landing`: reprodutibilidade da fonte
- `standardized`: padronização para reuso técnico
- `staging/profiling`: análise exploratória e diagnósticos
- `curated/analytics`: camada interna de engenharia
- `published/dashboard`: camada oficial de exposição controlada

## Responsabilidade por ambiente

- ambiente local: geração, inspeção, testes e reprodutibilidade do case
- GitHub Actions: validação contínua, policy checks e promoção da branch de deploy por ambiente
- Streamlit Cloud: consumo executivo publicado
- Dadosfera/Metabase: catálogo, ativo publicado e evidências externas

## Critério de operação saudável

Uma operação saudável deste projeto exige, ao mesmo tempo:

- docs centrais alinhadas ao fluxo real
- camada `published/dashboard` consistente com contratos e quality checks
- camada `published/semantic` materializada e coerente com o dashboard
- monitoramento de freshness da camada publicada sem alertas abertos
- branches `develop`, `release` e `main` íntegras conforme o estágio de promoção
- branch de deploy do ambiente alvo atualizada pelo fluxo de promoção
- app publicado carregando a versão esperada da camada minimizada no ambiente alvo

## Decisões de escopo

- o core do case está nas camadas de analytics engineering e dashboard
- artefatos bônus não mudam a operação principal do case
- integrações externas dependem de credencial e ambiente, então a automação local é a prova principal
