# Bônus de GenAI

## Objetivo do Bônus

Este bônus adiciona ao dashboard uma camada de experiência inspirada em copilotos analíticos, chamada `Insights Inteligentes`. A ideia é transformar o painel em um Data App mais próximo da tomada de decisão, e não apenas em uma coleção de gráficos.

Em vez de exigir que a pessoa usuária interprete manualmente cada visual, a seção sintetiza o recorte filtrado e entrega uma leitura executiva automática com foco em negócio.

## Problema de Negócio Atendido

Em contextos reais, um dos principais desafios de analytics não é apenas gerar dados ou gráficos, mas reduzir o tempo entre:

- observar um recorte
- entender o que ele significa
- decidir qual ação faz mais sentido

Mesmo quando o dashboard é bem construído, a leitura ainda depende de repertório analítico. Isso cria fricção para lideranças, stakeholders de negócio e perfis menos técnicos.

O bônus de GenAI ataca exatamente esse problema: aproximar os dados da decisão por meio de uma camada textual orientada a síntese, destaque de padrões e sugestão de próximos passos.

## Como o Data App Aproxima Dados e Decisão

A seção `Insights Inteligentes` atua como um copiloto analítico heurístico sobre o recorte filtrado do dashboard. Ela:

- lê o contexto dos filtros ativos
- identifica a categoria líder em receita
- interpreta a tendência temporal mais recente
- destaca a UF com maior peso comercial
- aponta o principal alerta logístico do recorte
- gera recomendações automáticas de negócio com base em regras heurísticas

Na prática, isso aproxima dados e decisão porque:

- reduz o esforço de interpretação inicial
- ajuda a transformar observação em narrativa executiva
- orienta o olhar do usuário para o que é mais importante naquele recorte
- deixa o dashboard mais próximo de uma ferramenta de apoio gerencial

## O que Foi Implementado no Projeto

No estado atual, o copiloto não depende de uma LLM externa. A geração dos insights acontece localmente, com regras determinísticas baseadas na `fact_orders_enriched`.

Isso traz algumas vantagens:

- funcionamento simples e reprodutível
- zero dependência de API externa
- custo operacional nulo
- comportamento previsível para apresentação do case

Ao mesmo tempo, a experiência já simula o papel de um assistente analítico, mostrando como o dashboard pode evoluir de visualização para interpretação assistida.

## Como uma LLM Poderia Ser Conectada Futuramente

Em uma evolução futura, essa camada poderia ser conectada a uma LLM para suportar perguntas em linguagem natural, como:

- "Quais categorias mais cresceram no período filtrado?"
- "Por que o atraso está alto neste recorte?"
- "Quais estados combinam alta receita e baixa satisfação?"
- "Resuma este painel para uma diretoria comercial."

Uma arquitetura simples para essa evolução seria:

1. capturar o contexto do filtro ativo no Streamlit
2. gerar um conjunto estruturado de métricas do recorte
3. montar um prompt com contexto de negócio, definição das métricas e regras de interpretação
4. enviar esse prompt para uma LLM
5. devolver a resposta no painel com linguagem executiva

## Caminhos Possíveis de Evolução

Com uma LLM integrada, o Data App poderia incluir:

- perguntas e respostas em linguagem natural sobre o recorte filtrado
- geração automática de sumários executivos por área
- explicação textual de anomalias e mudanças de tendência
- sugestão de hipóteses investigativas
- comparação entre períodos e segmentos com narrativa automática

Também seria possível adicionar salvaguardas, como:

- grounding em métricas calculadas localmente
- limitação de resposta a fatos presentes no dataset
- trilha de auditoria do prompt e da resposta
- avisos quando a resposta envolver inferência e não observação direta

## Valor Adicional para o Case

Este bônus aumenta o valor da entrega por mostrar que o projeto não termina na modelagem e na visualização tradicional. Ele demonstra uma visão de produto analítico, em que dados, interface e suporte à decisão caminham juntos.

Isso reforça três pontos relevantes no contexto de um case técnico:

- maturidade na transformação de dados em experiência de uso
- preocupação com adoção por públicos não técnicos
- visão prática de como analytics pode evoluir para GenAI com governança

Em resumo, o bônus posiciona o dashboard como um embrião de assistente analítico, aproximando a solução de um cenário real de Data App com linguagem natural e apoio à decisão.
