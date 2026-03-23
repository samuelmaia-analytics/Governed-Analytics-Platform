# 01 Contexto

Este documento funciona como ponto de entrada do case.

## Objetivo

Transformar o dataset Olist em uma solucao de dados ponta a ponta, cobrindo:

- ingestao
- padronizacao
- modelagem analitica
- qualidade
- SQL
- dashboard
- catalogacao
- documentacao

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

## Entregavel principal

O principal ativo do projeto e:

- `data/curated/analytics/fact_orders_enriched.parquet`

Essa tabela foi desenhada para consolidar o contexto analitico do case com granularidade de item de pedido.

## Leitura recomendada

- contexto geral do case: [README.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\README.md)
- narrativa principal: [docs/case_answers.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\case_answers.md)
- inventario da fonte: [docs/raw_data_inventory.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\raw_data_inventory.md)
