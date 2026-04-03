# Roteiro de Apresentação

## Mensagem Central

Este projeto não foi desenhado como exercício de visualização. Ele foi estruturado como um produto analítico operacionalizado: uma base transacional fragmentada foi convertida em um ativo confiável, governado e consumível por múltiplos canais, com operação recorrente da camada publicada.

## Abertura

“Este projeto foi organizado para responder a uma pergunta simples: como transformar um conjunto relacional bruto de e-commerce em um ativo analítico que suporte decisão de negócio sem perder rastreabilidade técnica. A resposta foi construir uma camada factual defensável, separar a exposição executiva da base interna e empacotar sua operação recorrente.”

## Problema

“O dataset Olist é rico, mas nasce fragmentado. Pedidos, itens, produtos, clientes, sellers, pagamentos e reviews não chegam prontos para leitura executiva. O problema real não era fazer joins; era criar uma camada estável o suficiente para responder perguntas de negócio com consistência, governança e possibilidade de consumo controlado.”

## Decisão Arquitetural

“A principal decisão foi preservar granularidade por item de pedido em `fact_orders_enriched`. Isso deu flexibilidade para SQL, qualidade, documentação e exportações sem distorcer análise. A segunda decisão foi separar essa base da camada publicada `fact_orders_dashboard`, para que o consumo executivo não dependesse da camada interna completa.”

## Modelagem e Qualidade

“A modelagem foi tratada como estrutura de produto, não como tabela final isolada. Além da tabela principal, o projeto inclui checks de qualidade, contratos simples de schema, classificação de dados, documentação de privacidade, CI, lint e testes automatizados. Isso importa porque a base não fica apenas utilizável; ela fica defensável.”

## Consumo Analítico

“Com essa base, o projeto responde perguntas concretas sobre concentração de receita, evolução temporal, geografia, atraso logístico e meios de pagamento. Essas respostas não estão escondidas em visualização. Elas existem em SQL versionada, resultados exportados e evidências reproduzíveis.”

## Dashboard

“O Streamlit é a camada executiva da solução. Ele consome exclusivamente a camada publicada e traduz a base em KPIs, tendência, categorias, geografia e insights. O ponto forte não é o visual em si; é a coerência entre modelagem, governança e produto.”

## Semântica Expandida

“A camada publicada passou a suportar também recortes de logística, seller e cohort. Isso mostra que a solução evolui sem precisar expor novamente a camada interna completa. A semântica cresce, mas a governança continua preservada.”

## Robustez Técnica

“No estado atual, o repositório sustenta `124` testes passando, cobertura total acima de `83%` e gate mínimo de `80%` em CI. Isso transforma o projeto em algo revisável por engenharia com muito menos risco de regressão silenciosa.”

## Operação da Camada Publicada

“Além da modelagem e da publicação, a camada publicada já conta com monitoramento recorrente de freshness e qualidade, além de um job agendado que gera artefatos operacionais. Isso eleva o projeto porque mostra preocupação com operação, e não apenas com geração manual do ativo.”

## Escopo Principal e Extensões

“O núcleo do projeto está em ingestão, padronização, modelagem, governança, publicação e dashboard. Power BI, GenAI e exportações complementares entram como extensões. Isso foi mantido explícito para não inflar o escopo além do que realmente sustenta o produto principal.”

## Fechamento

“A leitura correta deste projeto é: o produto analítico está pronto, a automação relevante já existe, a robustez de engenharia foi demonstrada e os próximos passos estão claramente separados do núcleo já implementado. Para um projeto técnico, isso mostra capacidade real de construir ativo, governar exposição e fechar a jornada entre engenharia e consumo.”

## Encerramento Sugerido

“Se eu resumir em uma frase: este projeto mostra menos um dashboard e mais um ativo analítico operacionalizado com critério.”
