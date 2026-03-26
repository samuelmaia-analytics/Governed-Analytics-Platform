# 05 Dashboard

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`

Este documento resume o dashboard final do case, sua fonte de dados, o link público de acesso e as evidências visuais do produto analítico.

## Aplicação

- app: `streamlit_app/app.py`
- link público: `https://samuelmaia-032026.streamlit.app/`
- fonte exclusiva:
  - `data/published/dashboard/fact_orders_dashboard.parquet`

## Ativo publicado equivalente

Para upload manual em plataforma e demonstração de publicação, o arquivo equivalente é:

- `data/published/dashboard/fact_orders_dashboard.csv`

Regra prática de uso:

- `parquet`: execução local do Streamlit
- `csv`: upload na Dadosfera

## Objetivo

Transformar a camada analítica publicada em leitura executiva de:

- KPIs
- tendência temporal
- categorias
- geografia
- operação
- insights

## Evidências

- dashboard online:
  - `https://samuelmaia-032026.streamlit.app/`
- screenshots finais do Streamlit:
  - `images/dashboard/01_overview.png`
  - `images/dashboard/02_kpis.png`
  - `images/dashboard/03_temporal.png`
  - `images/dashboard/04_categories.png`
  - `images/dashboard/05_geography.png`

## Valor do dashboard no case

O dashboard representa a camada de consumo executivo da solução. Ele não lê a base analítica interna diretamente; consome apenas o ativo publicado e minimizado, reforçando a coerência entre engenharia, governança e apresentação final.

## Referências detalhadas

- runbook de captura: [docs/streamlit_capture_runbook.md](./streamlit_capture_runbook.md)
- deck: [presentation/case_deck.md](../presentation/case_deck.md)


