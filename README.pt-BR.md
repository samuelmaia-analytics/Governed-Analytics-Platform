# Governed Analytics Platform

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/ci.yml)
[![Lint](https://img.shields.io/badge/Lint-Ruff-2D2D2D?logo=ruff&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/lint.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Coverage](https://codecov.io/gh/samuelmaia-analytics/Governed-Analytics-Platform/branch/main/graph/badge.svg)](https://codecov.io/gh/samuelmaia-analytics/Governed-Analytics-Platform)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live-red?logo=streamlit)](https://governed-analytics-platform.streamlit.app/)

**Idioma:** [English](README.md) | `Português`

Plataforma analítica governada para portfólio.
Foco em Analytics Engineering com controles de governança, qualidade e privacidade.

## Resumo executivo

Este repositório demonstra um fluxo completo:

1. ingestão e transformação de dados;
2. classificação de privacidade inspirada em LGPD;
3. avaliação de risco explicável;
4. validação de qualidade;
5. publicação controlada para consumo executivo.

## Impacto de negócio

- Reduz risco de exposição indevida ao separar camada interna e camada publicada.
- Aumenta confiança executiva com decisão explícita de publicação (`Approved`, `Needs Review`, `Blocked`).
- Melhora velocidade de revisão técnica com evidências automatizadas de qualidade e privacidade.
- Cria narrativa defensável para auditoria técnica com contratos, score de risco e relatórios.

## Como revisar este projeto em 5 minutos

1. Leia as seções de problema e solução.
2. Veja a arquitetura e a separação entre camadas.
3. Rode `make install`, `make test`, `make app`.
4. Abra o app e confira páginas de governança.
5. Revise `docs/privacy_governance.md` e `docs/semantic_layer.md`.

## Problema de negócio

Em muitos times, dashboards são publicados sem critérios claros de qualidade e privacidade.
Isso aumenta risco operacional, risco regulatório e perda de confiança.

## Solução

Abordagem de produto analítico governado:

- pipeline modular em Python;
- separação explícita entre camada interna e camada publicada;
- classificação e risco de privacidade;
- regras de qualidade em contrato;
- documentação operacional e executiva versionada.

## Implementado vs Simulado

### Implementado

- Pipeline Python modular com etapas reproduzíveis.
- Classificação LGPD por heurística e contrato YAML.
- Score de risco explicável e decisão de publicação.
- Regras de qualidade e checks automatizados.
- App Streamlit com visão executiva de decisão de publicação.
- Testes, lint, type-check e CI.

### Simulado

- Inventário de tratamento com controlador/operador/encarregado fictícios.
- Mini RIPD em Markdown para demonstração técnica.
- Base legal e retenção em linguagem de portfólio.
- Controles corporativos avançados (IAM completo e trilha centralizada de auditoria).

## Setup local

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
make test
make app
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
make install
copy .env.example .env
make test
make app
```

## Links

- Streamlit app: <https://governed-analytics-platform.streamlit.app/>
- Repositório: <https://github.com/samuelmaia-analytics/Governed-Analytics-Platform>
- Índice técnico: [docs/README.md](docs/README.md)
