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

O projeto já possui um manifesto local de catálogo e inventário de ativos. Além disso, o ativo principal foi publicado na Dadosfera com evidências visuais de importação, catálogo, coleção e volume acima de 100 mil linhas. O que ainda permanece pendente é a criação de um pipeline nativo na plataforma.

## Fechamento

Hoje o projeto já está forte como entrega de analytics engineering e data product, com GitHub consolidado e evidências reais do ativo principal na Dadosfera. O próximo passo é fechar a apresentação final e, se houver tempo, expandir a operacionalização para pipeline nativo na plataforma.
