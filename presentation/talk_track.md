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

Este projeto foi estruturado como um mini produto de dados, com separação por camadas, documentação, publicação de dataset, consultas SQL analíticas e visualização executiva.

Na Dadosfera, foi realizada a importação do ativo publicado, a documentação do dataset no catálogo e o registro das evidências da carga e do volume de dados.

Como resultado, a solução permite responder perguntas de negócio sobre receita, pedidos, ticket médio, categorias, atraso logístico, distribuição por status e recortes geográficos, apoiando tomada de decisão de forma mais clara e escalável.

Como próximos passos, a evolução natural da solução é ampliar o uso como Data App, fortalecer automações de catalogação e expandir a camada de leitura executiva assistida.
