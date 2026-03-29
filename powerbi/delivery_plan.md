# Plano de Materialização do Bônus em Power BI


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

## Status Atual

O projeto já possui os datasets necessários para montar o bônus em Power BI:

- `data/processed/bi_exports/fact_sales_power_bi.csv`
- `data/processed/bi_exports/dim_date.csv`
- `data/processed/bi_exports/dim_product.csv`
- `data/processed/bi_exports/dim_customer.csv`
- `data/processed/bi_exports/dim_seller.csv`
- `data/processed/bi_exports/dim_payment.csv`
- `data/processed/bi_exports/dim_order_status.csv`

Isso significa que a camada de dados para o bônus está pronta localmente.

## O que ainda falta

- revisar o arquivo `.pbix` atual, se houver ajuste final antes de versionamento
- validar manualmente os números e filtros no Power BI Desktop
- manter screenshots finais consistentes com a versão mais recente do dashboard

## Estrutura recomendada nesta pasta

- `dashboard_overview.pbix`
- `dashboard_overview.png`
- `dashboard_drilldown.png`
- `measures.md`

## Página mínima recomendada

- cards de KPI:
  - receita total
  - pedidos
  - ticket médio
  - percentual de atraso
  - review medio
- linha:
  - receita mensal
- barras:
  - top categorias
- mapa ou barras:
  - receita por estado
- donut:
  - mix por pagamento

## Status correto para a apresentação

Como o `.pbix` já existe no repositório, o bônus deve ser descrito como:

- `bônus de Power BI materializado com arquivo e screenshots`
- `validação final dependente de revisão manual no Power BI Desktop`
