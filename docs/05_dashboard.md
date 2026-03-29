# 05 Dashboard

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento descreve o dashboard final do case como camada oficial de consumo executivo, explicando a origem dos dados, a lógica de exposição e a leitura de negócio que o app sustenta.

## Tese do Dashboard

O dashboard não é um front-end conectado diretamente à camada analítica interna. Ele existe para consumir a camada publicada `fact_orders_dashboard`, com governança, minimização e chaves pseudonimizadas, preservando coerência entre engenharia, publicação e consumo.

Essa escolha é central para o case porque:

- desacopla consumo executivo da base analítica interna
- reduz exposição desnecessária de identificadores e localidade fina
- mantém o Streamlit alinhado ao ativo publicado na plataforma
- permite evoluir semântica e monitoramento sem alterar a lógica do app como fonte oficial de leitura

## Fontes de Dados do App

### Fonte principal

- `data/published/dashboard/fact_orders_dashboard.parquet`

### Fonte equivalente para upload manual em plataforma

- `data/published/dashboard/fact_orders_dashboard.csv`

### Camadas complementares já materializadas no projeto

- `data/published/semantic/logistics_slice.parquet`
- `data/published/semantic/seller_slice.parquet`
- `data/published/semantic/cohort_slice.parquet`
- `data/published/monitoring/published_layer_monitoring.csv`

Regra prática:

- `published/dashboard`: fonte oficial do app e do consumo executivo
- `published/semantic`: marts publicados para novos recortes analíticos
- `published/monitoring`: operação e observabilidade da camada publicada

No estado atual do projeto, o Streamlit continua tendo `published/dashboard` como base principal, mas também passou a ler:

- `published/monitoring` para exibir o bloco de saúde operacional da camada publicada
- `published/semantic` para exibir os recortes publicados de logística, seller e cohort

## Perguntas de Negócio que o Dashboard Responde

- qual é o nível atual de receita, ticket e atraso
- como a receita evolui ao longo do tempo
- quais categorias concentram valor e pressão logística
- quais estados concentram receita e pior performance operacional
- como os meios de pagamento se distribuem

Além disso, a evolução recente da camada publicada passou a permitir desdobramentos em:

- cohort e recorrência de compra
- recortes por seller pseudonimizado
- leitura mais detalhada de despacho, transporte e peso relativo do frete
- leitura do status operacional mais recente da camada publicada sem sair do app

## Decisões de Design Analítico

- o app consome apenas `published/dashboard`, nunca `curated/analytics`
- o app pode enriquecer a leitura com `published/monitoring` e `published/semantic`, mas sem depender da camada interna
- a navegação é organizada por perguntas executivas, não por tabela de origem
- a visualização prioriza velocidade de leitura e capacidade de filtro
- a cauda longa de categorias é resumida quando isso melhora clareza visual
- recortes mais granulares permanecem na camada analítica interna ou nos marts semânticos publicados

## Leitura Correta da Arquitetura de Consumo

O Streamlit é a camada oficial de exposição executiva do projeto. Isso significa:

- o dado já chega ao app tratado para consumo
- o dashboard não precisa replicar regras pesadas de transformação
- qualidade, contratos e governança acontecem antes da etapa de visualização
- a mesma camada publicada sustenta o app e a publicação evidenciada na Dadosfera
- monitoramento e semântica entram no app como extensões publicadas, não como atalhos para a camada interna

Esse desenho aproxima o case de um produto analítico real, e não apenas de uma interface sobre a base inteira.

## Valor do Dashboard no Case

O valor do dashboard não está apenas na estética ou nos gráficos. Ele materializa a etapa final da arquitetura: transformar uma camada publicada segura em leitura executiva utilizável.

Em termos de avaliação, isso demonstra:

- capacidade de modelar para consumo e não apenas para exploração
- critério de exposição de dados
- alinhamento entre arquitetura, visualização e governança
- preocupação com reuso do ativo publicado fora do app
- capacidade de levar operação e semântica para a interface executiva sem romper a separação entre camadas

## Tradeoff Explícito

O dashboard abre mão de expor toda a riqueza da camada interna para ganhar:

- governança
- simplicidade de leitura
- menor risco de exposição
- consistência com o ativo publicado externamente

Essa é uma decisão deliberada. A profundidade exploratória continua existindo, mas não é a função da camada de consumo executivo.

## Evidências

### Dashboard online

- `https://samuelmaia-032026.streamlit.app/`

### Screenshots finais do app

- `images/dashboard/01_overview.png`
- `images/dashboard/02_kpis.png`
- `images/dashboard/03_temporal.png`
- `images/dashboard/04_categories.png`
- `images/dashboard/05_geography.png`

## Referências

- runbook de captura: [docs/streamlit_capture_runbook.md](./streamlit_capture_runbook.md)
- operação do projeto: [docs/operating_model.md](./operating_model.md)
- publicação segura: [docs/privacy_governance.md](./privacy_governance.md)
- deck: [presentation/case_deck.md](../presentation/case_deck.md)
