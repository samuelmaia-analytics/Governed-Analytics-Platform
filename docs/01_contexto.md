# 01 Contexto

Este documento funciona como ponto de entrada do case.

## Objetivo

Transformar o dataset Olist em uma solução de dados ponta a ponta, cobrindo:

- ingestao
- padronizacao
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

## Entregavel principal

O principal ativo do projeto e:

- `data/curated/analytics/fact_orders_enriched.parquet`

Essa tabela foi desenhada para consolidar o contexto analítico do case com granularidade de item de pedido.

## Leitura recomendada

- contexto geral do case: [README.md](../README.md)
- narrativa principal: [docs/case_answers.md](./case_answers.md)
- inventário da fonte: [docs/raw_data_inventory.md](./raw_data_inventory.md)



