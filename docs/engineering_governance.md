# Engineering Governance

Este documento consolida os guardrails operacionais do repositório para elevar o padrão de manutenção sem ampliar indevidamente o escopo do case.

## Guardrails de Entrega

- `CI`: executa testes automatizados e smoke check do entrypoint do pipeline.
- `Lint`: valida estilo e erros estáticos com Ruff.
- `Deploy Streamlit`: reaplica os guardrails antes de promover o branch `streamlit-prod`.
- `Operate Published Layer`: executa build, publicação, expansão semântica, monitoramento e upload de artefatos operacionais.
- `Dependabot`: monitora dependências Python e GitHub Actions.

## Guardrails de Repositório

- `CODEOWNERS` define ownership mínimo das áreas críticas.
- `CONTRIBUTING.md` padroniza o fluxo de contribuição e validação local.
- `SECURITY.md` registra o tratamento esperado para incidentes e exposição indevida.

## Decisões de Escopo

- Não foram adicionados orquestradores, camadas de infraestrutura ou controles corporativos completos.
- O reforço foi concentrado em confiabilidade de entrega, rastreabilidade e governança leve.
- O objetivo continua sendo demonstrar analytics engineering orientado a produto no contexto do case.
