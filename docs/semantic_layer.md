# Camada Semantica Expandida

A camada published passa a expor marts operacionais para recortes de logistica, seller e cohort.

Esses ativos nao ficam restritos a uso tecnico: quando publicados no ambiente do app, tambem passam a alimentar a secao semantica do Streamlit, ampliando a leitura executiva sem reintroduzir dependencias da camada interna.

## Ativos Gerados

- `logistics_slice`: **3,821** linhas
- `seller_slice`: **3,095** linhas
- `cohort_slice`: **220** linhas

## Recortes Disponiveis

- Logistica: tempo medio de entrega, despacho, transporte e peso relativo do frete por UF origem/destino e mes.
- Seller: tier de volume, atraso medio, entrega media, ticket medio e satisfacao por seller pseudonimizado.
- Cohort: comportamento por cohort de compra e maturacao mensal da base de clientes.

## Consumo no App

- o Streamlit continua tendo `fact_orders_dashboard` como base principal
- quando os arquivos de `published/semantic` estao versionados no ambiente, o app exibe os recortes em uma secao propria
- a ausencia desses arquivos nao derruba a aplicacao; o app entra em modo degradado com mensagem explicita
