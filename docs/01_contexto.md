# 01 Contexto

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento funciona como ponto de entrada do case e resume o problema, o escopo e o ativo analítico principal.

## Objetivo

Transformar o dataset Olist em uma solução de dados ponta a ponta, cobrindo:

- ingestão
- padronização
- modelagem analítica
- qualidade
- SQL
- dashboard
- catalogação
- documentação

## Dataset escolhido

- fonte: `Brazilian E-Commerce Public Dataset by Olist`
- natureza: dados transacionais de e-commerce
- entidades principais:
  - pedidos
  - itens de pedido
  - clientes
  - produtos
  - sellers
  - pagamentos
  - reviews

## Entregável principal

O principal ativo do projeto é:

- `data/curated/analytics/fact_orders_enriched.parquet`

Essa tabela foi desenhada para consolidar o contexto analítico do case com granularidade de item de pedido, preservando detalhe operacional sem comprometer leitura executiva.

## Leitura recomendada

- contexto geral do case: [README.md](../README.md)
- narrativa principal: [docs/case_answers.md](./case_answers.md)
- inventário da fonte: [docs/raw_data_inventory.md](./raw_data_inventory.md)



