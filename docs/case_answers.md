# Respostas do Case

## Resumo Executivo

Este projeto transforma o dataset Olist em um produto analítico utilizável, com separação clara entre camada interna de engenharia e camada publicada para consumo executivo. O núcleo técnico da entrega é `fact_orders_enriched`, uma fato com granularidade de item de pedido e `112.650` registros, construída para responder perguntas de negócio sem sacrificar rastreabilidade técnica.

A camada derivada `fact_orders_dashboard` reduz risco de exposição, preserva utilidade analítica e serve como fonte oficial do Streamlit e do ativo publicado. Isso dá ao case um desenho mais maduro do que uma entrega centrada apenas em visualização.

## Tese da Entrega

O valor desta entrega está em combinar quatro frentes que normalmente aparecem desconectadas em cases:

- modelagem com granularidade defensável
- qualidade e governança explícitas
- consumo real por múltiplos canais
- documentação suficiente para auditoria e defesa técnica

O projeto não depende de narrativa inflada. Ele sustenta avaliação porque conecta decisão de modelagem, produto analítico, evidência operacional e automação mínima de engenharia em um mesmo fluxo.

## Estado Real da Solução

| Ambiente | Estado | Evidência |
| --- | --- | --- |
| Repositório local | concluído | pipeline, testes, docs, SQL, dashboard e artefatos |
| GitHub | concluído | documentação, workflows e automação versionados |
| Dadosfera/Metabase | concluído para publicação e catálogo | ativo publicado, coleção evidenciada, links reais e sync por API |
| Dadosfera nativa como motor de pipeline | parcialmente preparada | há operador via API e template versionado, mas não há execução nativa comprovada no tenant |

Leitura correta:

- o produto analítico está entregue
- a publicação externa está comprovada
- a integração programática de catálogo está implementada
- o que segue sem comprovação final é pipeline nativo executando dentro da plataforma

## Problema de Negócio

O dataset Olist é relacional, fragmentado e operacional. Sozinho, ele não responde bem perguntas de negócio sobre receita, atraso, categoria, pagamento, geografia e experiência do cliente. O problema real não é apenas juntar tabelas; é transformar eventos transacionais em uma camada confiável e reutilizável para análise, sem perder coerência entre dado, consumo e governança.

Foi por isso que a solução foi desenhada como produto analítico, não como notebook exploratório.

## Decisões de Modelagem

A decisão estrutural mais importante foi usar `order_items` como base factual. Isso preserva o nível em que preço, frete, produto, seller e entrega fazem sentido analítico. `orders`, `customers`, `products` e `sellers` entram como enriquecimento dimensional, enquanto `payments` e `reviews` são agregados antes do join para evitar multiplicação artificial de linhas.

Essa escolha sustenta duas qualidades que importam em avaliação senior:

- integridade analítica: a granularidade é estável e defensável
- flexibilidade de consumo: a mesma base atende SQL, qualidade, dashboard e export BI

## Arquitetura de Publicação

O projeto separa explicitamente:

- `fact_orders_enriched`: camada interna para engenharia, SQL, qualidade e auditoria
- `fact_orders_dashboard`: camada publicada para consumo executivo

Essa separação não é cosmética. Ela reduz acoplamento, melhora governança e impede que o dashboard dependa de atributos desnecessários ou sensíveis. Na publicada, identificadores são pseudonimizados e campos como cidade, CEP e IDs operacionais deixam de ser expostos quando não agregam valor ao caso de uso.

## Perguntas de Negócio Respondidas

As consultas SQL e o dashboard respondem, de forma consistente, a cinco frentes principais:

- quais categorias concentram receita
- como receita e atraso evoluem no tempo
- onde a receita se concentra geograficamente
- quais categorias sofrem mais pressão logística
- como os meios de pagamento se distribuem

Essas respostas não dependem de lógica escondida em visual. Elas partem de uma fato documentada, queries versionadas e resultados exportados, o que melhora auditabilidade.

## Leitura Executiva dos Resultados

Os resultados mostram uma operação com forte concentração em poucas categorias e poucos estados, crescimento relevante ao longo do tempo e dependência marcante de `credit_card` como meio de pagamento dominante. Também deixam claro que crescimento comercial e pressão operacional coexistem: meses de pico ampliam receita, mas também expõem gargalos de atraso.

Do ponto de vista gerencial, isso sugere três leituras prioritárias:

- concentração de valor pede foco em categorias e geografias de maior peso
- sazonalidade precisa ser lida junto com performance logística
- atraso deve ser tratado como problema econômico e de experiência, não apenas operacional

## Dadosfera, Catálogo e Automação

O projeto já vai além de um manifesto local. Hoje ele possui:

- ativo principal publicado e evidenciado na Dadosfera/Metabase
- coleção publicada com evidências versionadas
- manifesto local da coleção e inventário de ativos
- sincronização programática de ativos públicos via API do Maestro
- preparação operacional para criação e execução de pipelines nativos via API
- automação de promoção do branch de deploy do Streamlit

Essa combinação é importante porque demonstra que a entrega não termina na geração da base. Ela cobre também a etapa em que muitos projetos falham: tornar o ativo encontrável, publicável e reutilizável.

## O Que Não Está Sendo Superestimado

Alguns limites permanecem intencionais e precisam ser mantidos claros:

- não há pipeline nativo comprovadamente executando dentro da Dadosfera
- há preparação operacional para pipeline nativo via API, mas sem evidência de run final no tenant
- a plataforma ainda não substitui o motor local de transformação
- o bônus de GenAI existe como enriquecimento e prova de capacidade, não como eixo central da solução

Essa postura é parte da qualidade da entrega. Um case senior não infla maturidade operacional onde não há evidência.

## Por Que Esta Entrega É Forte

Esta entrega é forte porque demonstra critério. O projeto não tenta parecer uma plataforma completa; ele mostra capacidade real de estruturar dados, modelar uma fato útil, controlar exposição, publicar ativos, documentar decisões e automatizar o suficiente para sair do artesanal.

Em termos de avaliação, isso sinaliza:

- domínio de analytics engineering
- noção de data product
- maturidade de governança acima da média para case técnico
- capacidade de transformar output analítico em ativo defendível

## Próximos Passos Naturais

- implementar pipeline nativo na Dadosfera, se houver exigência de aprofundamento
- expandir o sync de catálogo para mais tipos de ativos
- transformar a preparação operacional de pipeline via API em execução real com evidência de run e output
- incluir marts adicionais por cliente, seller e categoria
- ampliar testes para regressão analítica e componentes de consumo
- evoluir métricas para cohort, recorrência e valor por cliente

## Conclusão

O projeto atende ao case porque entrega uma solução de dados ponta a ponta com coerência entre engenharia, governança, consumo e evidência. Ele sai do dado bruto, constrói uma camada analítica defensável, publica uma versão segura para consumo executivo e prova o valor da solução em canais diferentes sem perder consistência.

A síntese correta é simples: o produto analítico está pronto, a publicação está comprovada, a automação relevante já existe, a preparação para pipeline nativo via API foi implementada, e o limite estrutural remanescente é a ausência de execução nativa comprovada dentro da plataforma.
