# Camada Semantica Expandida

A camada published passa a expor marts operacionais e executivos para recortes de logistica, seller, cohort, categoria e geografia.

O ativo `executive_kpis_slice` tambem passou a ser consumido diretamente pelo dashboard Streamlit para os cards principais, reduzindo dependencia de calculos locais no app e reforcando a camada semantica como contrato executivo reutilizavel.

O repositório agora também possui uma camada dbt complementar sobre os ativos Python confiáveis. Essa camada não substitui os artefatos publicados abaixo; ela adiciona documentação, testes, lineage e marts SQL equivalentes para consumo governado.

## Ativos Gerados

- `logistics_slice`: **3,821** linhas
- `seller_slice`: **3,095** linhas
- `cohort_slice`: **220** linhas
- `category_slice`: **3,263** linhas
- `state_performance_slice`: **559** linhas
- `executive_kpis_slice`: **8** linhas

## Recortes Disponiveis

- Logistica: tempo medio de entrega, despacho, transporte e peso relativo do frete por UF origem/destino e mes.
- Seller: tier de volume, atraso medio, entrega media, ticket medio e satisfacao por seller pseudonimizado.
- Cohort: comportamento por cohort de compra e maturacao mensal da base de clientes.
- Categoria: receita, ticket, atraso, review e meio de pagamento por categoria e mes.
- Geografia executiva: receita, sellers ativos, atraso e satisfacao por UF e mes.
- KPIs executivos: receita, pedidos, clientes, ticket, prazo, atraso, review e frete medio em um ativo resumido e reutilizavel.

## Consumo Executivo

- `executive_kpis_slice` e o ativo preferencial para os KPIs principais do Streamlit.
- O app continua com fallback para calculo local apenas como mecanismo de resiliencia.
- A mesma estrutura pode ser reaproveitada por Power BI, scorecards futuros e integracoes GenAI auditaveis.

## Relacao com o dbt

- Python continua materializando os slices publicados em `data/published/semantic/`
- dbt organiza a camada semântica em um grafo documentado sobre `fact_orders_enriched` e `fact_orders_dashboard`
- marts como `mart_executive_kpis`, `mart_category_performance`, `mart_state_performance`, `mart_logistics_performance`, `mart_seller_performance` e `mart_customer_cohorts` reforçam esse contrato semântico para consumidores SQL e documentação
- a leitura de lineage está resumida em `docs/dbt_lineage.md`
