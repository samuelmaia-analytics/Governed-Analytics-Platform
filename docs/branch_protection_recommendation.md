# Branch Protection Recommendation

Este documento registra a configuração recomendada no GitHub para aproximar o repositório de um padrão corporativo de merge e release.

## Recomendação para `main`

- exigir pull request antes de merge
- exigir pelo menos 1 review
- exigir `CI` e `Lint` verdes
- bloquear merge com conversas não resolvidas
- bloquear force push
- bloquear delete da branch

## Recomendação para deploy

- usar `streamlit-production` como environment protegido
- restringir segredos ao environment
- exigir approval manual quando a alteração impactar deploy ou publicação

## Objetivo

- reduzir regressão em branch principal
- reforçar accountability
- alinhar a automação do repositório com a narrativa de governança do case
