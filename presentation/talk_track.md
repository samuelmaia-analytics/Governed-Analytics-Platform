# Talk Track

## Abertura

Este case parte do dataset Olist e tem como objetivo transformar dados transacionais brutos em um ativo analítico confiável, documentado e pronto para consumo executivo.

## Problema

O dataset está fragmentado em várias tabelas. O desafio foi organizar isso em uma solução ponta a ponta, com qualidade, rastreabilidade e leitura de negócio.

## O que eu construí

Eu implementei um pipeline em camadas, saindo de `raw` para `standardized`, depois `staging`, `curated` e por fim uma camada `published` para o dashboard.

## Ativo principal

O principal resultado é a `fact_orders_enriched`, com `112.650` linhas e granularidade de item de pedido. Essa tabela concentra pedidos, produtos, clientes, sellers, pagamentos e reviews.

## Qualidade e governança

Além da modelagem, eu adicionei checks de qualidade, contratos simples de schema, documentação de privacidade e uma separação clara entre camada interna e camada publicada.

## SQL e insights

Com essa base, eu respondi perguntas de negócio sobre receita por categoria, evolução temporal, receita por estado, atraso logístico e meios de pagamento.

## Dashboard

Para consumo executivo, eu publiquei uma camada reduzida e pseudonimizada e construí um dashboard Streamlit com KPIs, filtros globais, análise temporal, categorias, geografia e insights executivos.

## Dadosfera

O projeto já possui um manifesto local de catálogo e inventário de ativos. A parte que ainda precisa ser materializada de forma real é a publicação e evidência desses ativos dentro da plataforma Dadosfera.

## Fechamento

Hoje o projeto já está forte como entrega local de analytics engineering e data product. O próximo passo é fechar a operacionalização final: evidências visuais, plataforma e entrega consolidada no GitHub.
