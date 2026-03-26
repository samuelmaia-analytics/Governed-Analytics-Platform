# Roteiro de Apresentação

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`

## Abertura

Eu apresentaria este case como uma jornada completa de dados. A ideia não foi apenas montar um dashboard, mas mostrar como sair de dados transacionais brutos e chegar a um ativo analítico confiável, documentado e pronto para consumo.

## Problema

O Olist é um dataset muito rico, mas ele não chega pronto para leitura executiva. Os dados estão fragmentados em várias tabelas, então o desafio foi organizar essa base de um jeito que sustentasse análise de negócio com qualidade, rastreabilidade e clareza.

## O que eu construí

Eu implementei um pipeline em camadas, saindo de `raw` para `standardized`, depois `staging`, `curated` e, por fim, uma camada `published` voltada para consumo. Essa estrutura ajudou a separar bem o dado bruto, o dado tratado, a base analítica interna e o ativo publicado.

## Ativo principal

O principal resultado é a `fact_orders_enriched`, com `112.650` linhas e granularidade de item de pedido. Essa tabela concentra pedidos, produtos, clientes, sellers, pagamentos e reviews em uma estrutura que já responde às perguntas mais importantes do case.

## Qualidade e governança

Além da modelagem, eu adicionei checks de qualidade, contratos simples de schema, documentação de privacidade e uma separação clara entre camada interna e camada publicada. Isso foi importante para mostrar que a solução não é só visualmente funcional, mas tecnicamente defensável.

## SQL e insights

Com essa base, eu respondi perguntas de negócio sobre receita por categoria, evolução temporal, receita por estado, atraso logístico e meios de pagamento. Esse ponto é importante porque mostra que a modelagem realmente chegou em consumo analítico reproduzível.

## Dashboard

Para consumo executivo, eu publiquei uma camada reduzida e pseudonimizada e construí um dashboard Streamlit com KPIs, análise temporal, categorias, geografia e insights. A proposta foi dar uma leitura rápida do negócio, mantendo consistência com a base publicada. O link do app é `https://samuelmaia-032026.streamlit.app/`.

## Dadosfera

Além do repositório, o ativo principal foi publicado na Dadosfera com evidências visuais de importação, catálogo, coleção e volume acima de 100 mil linhas. O ponto que eu deixaria claro na apresentação é que isso já comprova a publicação do ativo, mas ainda não representa pipeline nativo executado dentro da plataforma.

## Fechamento

Eu encerraria dizendo que este projeto foi estruturado como um mini produto de dados. Ele combina pipeline, modelagem, qualidade, publicação, SQL e visualização executiva em uma entrega única.

Na prática, o case mostra capacidade de transformar dado bruto em ativo analítico utilizável. E, na minha leitura, a principal prova de valor da Dadosfera aqui é justamente acelerar a passagem entre engenharia, publicação e consumo, com mais governança e menos atrito operacional.

Como próximos passos, a evolução natural da solução é ampliar o uso como Data App, fortalecer automações de publicação e aprofundar a camada de leitura executiva assistida.
