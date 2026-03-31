# Branch Protection Recommendation

Este documento registra a configuração recomendada no GitHub para aproximar o repositório de um padrão corporativo de merge e release.

## Recomendação por branch

### `develop`

- exigir pull request antes de merge
- exigir pelo menos 1 review
- exigir `CI` e `Lint` verdes
- bloquear merge com conversas não resolvidas
- bloquear force push
- bloquear delete da branch

### `release`

- exigir pull request antes de merge
- exigir pelo menos 1 review
- exigir `CI` e `Lint` verdes
- bloquear merge com conversas não resolvidas
- bloquear force push
- bloquear delete da branch

### `main`

- exigir pull request antes de merge
- exigir pelo menos 1 review
- exigir `CI` e `Lint` verdes
- bloquear merge com conversas não resolvidas
- bloquear force push
- bloquear delete da branch

## Recomendação para deploy

- usar `streamlit-development`, `streamlit-staging` e `streamlit-production` como environments explícitos
- restringir segredos ao environment
- exigir approval manual em `stage` e `prod`
- manter o mapeamento branch -> ambiente -> deploy branch:
- `develop` -> `dev` -> `streamlit-dev`
- `release` -> `stage` -> `streamlit-stage`
- `main` -> `prod` -> `streamlit-prod`

## Contrato versionado

- a política canônica do repositório está em `contracts/governance/release_governance.json`
- a validação local pode ser executada com `python src/governance_validation.py`

## Objetivo

- reduzir regressão em branch principal
- reforçar accountability
- alinhar a automação do repositório com a narrativa de governança do case
