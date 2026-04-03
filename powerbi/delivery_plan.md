# Plano de Materialização do Bônus em Power BI


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/olist-governed-analytics-platform`
- App Streamlit: `https://olist-governed-analytics-platform.streamlit.app/`
- Dashboard Power BI: `https://app.powerbi.com/links/Xto6lIUiRF?ctid=b1b9d429-7862-4440-a25b-6ca19f868f47&pbi_source=linkShare`

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
