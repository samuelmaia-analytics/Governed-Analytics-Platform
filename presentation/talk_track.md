# Roteiro de Apresentação

## Mensagem central

Este case não foi desenhado como exercício de visualização. Ele foi estruturado como um produto analítico: uma base transacional fragmentada foi convertida em um ativo confiável, governado e consumível por múltiplos canais, com evidência real de publicação.

## Abertura

“Esta entrega foi organizada para responder a uma pergunta simples: como transformar um conjunto relacional bruto de e-commerce em um ativo analítico que suporte decisão de negócio sem perder rastreabilidade técnica. A resposta foi construir uma camada factual defensável, separar a exposição executiva da base interna e provar consumo real em dashboard, catálogo e BI.”

## Problema

“O dataset Olist é rico, mas nasce fragmentado. Pedidos, itens, produtos, clientes, sellers, pagamentos e reviews não chegam prontos para leitura executiva. O problema real não era fazer joins; era criar uma camada estável o suficiente para responder perguntas de negócio com consistência e governança.”

## Decisão arquitetural

“A principal decisão foi preservar granularidade por item de pedido em `fact_orders_enriched`. Isso deu flexibilidade para SQL, qualidade, documentação e exportações sem distorcer análise. A segunda decisão foi separar essa base da camada publicada `fact_orders_dashboard`, para que o consumo executivo não dependesse da camada interna completa.”

## Modelagem e qualidade

“A modelagem foi tratada como estrutura de produto, não como tabela final isolada. Além da fato principal, o projeto inclui checks de qualidade, contratos simples de schema, classificação de dados, documentação de privacidade, CI, lint e testes automatizados. Isso importa porque a base não fica apenas utilizável; ela fica defensável.”

## Consumo analítico

“Com essa base, o projeto responde perguntas concretas sobre concentração de receita, evolução temporal, geografia, atraso logístico e meios de pagamento. O importante aqui é que as respostas não estão escondidas em visualização. Elas existem em SQL versionada, resultados exportados e evidências reproduzíveis.”

## Dashboard

“O Streamlit é a camada executiva da solução. Ele consome exclusivamente a camada publicada e traduz a base em KPIs, tendência, categorias, geografia e insights. O ponto forte não é o visual em si; é a coerência entre modelagem, governança e produto.”

## Robustez técnica

“No estado final, o repositório sustenta `114` testes passando, cobertura total acima de `86%` e gate mínimo de `80%` em CI. Isso é relevante porque transforma o case em algo revisável por engenharia com muito menos risco de regressão silenciosa.”

## Dadosfera

“Além do ambiente local, o ativo principal foi publicado na Dadosfera/Metabase e está documentado com evidências visuais de importação, catálogo, coleção e volume. O repositório também inclui sincronização complementar de catálogo via API do Maestro. O que não se afirma é pipeline nativo rodando dentro da plataforma, porque isso não está comprovado.”

## Escopo core vs bônus

“O escopo core do case está em ingestão, padronização, modelagem, governança, publicação e dashboard. Power BI, GenAI e exportações complementares entram como extensões. Isso foi mantido explícito para não inflar o escopo além do que realmente sustenta o produto principal.”

## Fechamento

“A leitura correta desta entrega é: o produto analítico está pronto, a publicação está comprovada, a automação relevante já existe, a robustez de engenharia foi demonstrada e o único limite estrutural remanescente é a ausência de pipeline nativo dentro da plataforma. Para um case técnico, isso mostra capacidade real de construir ativo, governar exposição e fechar a jornada entre engenharia e consumo.”

## Encerramento sugerido

“Se eu resumir em uma frase: esta entrega mostra menos um dashboard e mais um ativo analítico operacionalizado com critério.”
