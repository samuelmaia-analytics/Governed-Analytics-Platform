# 05 Dashboard

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

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

## Decisões de design analítico

- o app consome apenas `published/dashboard`, nunca a camada `curated`
- a navegação foi separada por perguntas executivas, não por tabela de origem
- os visuais priorizam leitura rápida, concentração de valor, risco operacional e possibilidade de filtro
- quando há agregação de cauda longa em categoria, isso é assumido como decisão de clareza visual, não como detalhe escondido

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

## Tradeoff explícito

O dashboard abre mão de expor toda a riqueza da camada analítica interna para ganhar governança, simplicidade de leitura e menor risco de exposição desnecessária. Essa escolha é intencional: a profundidade exploratória permanece na camada `curated`, enquanto o Streamlit funciona como camada oficial de consumo executivo.

## Referências detalhadas

- runbook de captura: [docs/streamlit_capture_runbook.md](./streamlit_capture_runbook.md)
- deck: [presentation/case_deck.md](../presentation/case_deck.md)


