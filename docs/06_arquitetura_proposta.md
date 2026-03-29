# 06 Arquitetura Proposta


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento resume a arquitetura implementada e a evolução proposta com uso de plataforma.

## Arquitetura implementada

```text
raw -> standardized -> staging -> curated -> published -> dashboard
```

## Arquitetura proposta para evolução

```text
fontes -> plataforma / catalogação -> ativos publicados -> consumo por app, SQL e BI
```

## Referencias principais

- arquitetura atual: `docs/architecture.md`
- contexto de plataforma: `docs/about_dadosfera.md`

## Status atual

- arquitetura local: implementada
- evolução real na plataforma: depende de execução e evidência externa


