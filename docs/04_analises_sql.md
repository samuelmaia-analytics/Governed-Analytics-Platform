# 04 Análises SQL

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/Governed-Analytics-Platform`
- Dashboard Streamlit: `https://governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento aponta para os artefatos SQL principais do projeto e conecta a modelagem analítica às perguntas de negócio respondidas na solução.

## Perguntas respondidas

- quais categorias geram mais receita
- como a receita evolui no tempo
- como a receita se distribui por estado
- quais categorias sofrem mais atraso
- como os meios de pagamento se distribuem

## Queries principais

- `sql/01_exploracao_inicial.sql`
- `sql/02_limpeza.sql`
- `sql/03_kpis.sql`
- `sql/04_series_temporais.sql`
- `sql/05_categorias.sql`

## Resultados materializados

- `data/curated/query_results/`
- `data/screenshots/query_results/`

## Leitura recomendada

- começar pela query principal em `sql/query_principal.sql`
- usar `powerbi/evidencia_query.md` como síntese executiva dos resultados
- consultar `data/screenshots/query_results/` quando a evidência visual tabular for necessária

## Referências detalhadas

- narrativa analítica: [docs/technical_narrative.md](./technical_narrative.md)
- screenshots tabulares: [docs/imagens/README.md](./imagens/README.md)




