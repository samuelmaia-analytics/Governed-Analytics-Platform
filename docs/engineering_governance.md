# Engineering Governance

Este documento consolida os guardrails operacionais do repositório para elevar o padrão de manutenção sem ampliar indevidamente o escopo do case.

## Guardrails de Entrega

- `CI`: executa testes automatizados, smoke check do entrypoint do pipeline e validação do contrato de governança.
- `Lint`: valida estilo e erros estáticos com Ruff.
- `Policy Check`: valida os workflows reais contra o contrato versionado de governança.
- `Deploy Streamlit`: reaplica os guardrails antes de promover o branch de deploy do ambiente alvo.
- `Operate Published Layer`: executa build, publicação, expansão semântica, monitoramento e upload de artefatos operacionais.
- `Dependabot`: monitora dependências Python e GitHub Actions.

## Governança de Release

- `contracts/governance/release_governance.json` define a política canônica de branches, ambientes e workflows.
- `src/release_management.py` resolve o plano de promoção entre `dev`, `stage` e `prod`.
- `src/governance_validation.py` valida a coerência do contrato de release.
- `src/workflow_policy_validation.py` valida os gatilhos e branches dos workflows contra o contrato.
- `develop`, `release` e `main` representam, respectivamente, os estágios `dev`, `stage` e `prod`.
- `streamlit-dev`, `streamlit-stage` e `streamlit-prod` são branches de deploy, não branches de desenvolvimento.

## Guardrails de Repositório

- `CODEOWNERS` define ownership mínimo das áreas críticas.
- `CONTRIBUTING.md` padroniza o fluxo de contribuição e validação local.
- `SECURITY.md` registra o tratamento esperado para incidentes e exposição indevida.

## Decisões de Escopo

- Não foram adicionados orquestradores, camadas de infraestrutura ou controles corporativos completos.
- O reforço foi concentrado em confiabilidade de entrega, rastreabilidade e governança leve.
- O objetivo continua sendo demonstrar analytics engineering orientado a produto no contexto do case.
