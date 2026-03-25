# Plano de Materialização do Bônus em Power BI

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

- criar o arquivo `.pbix`
- montar ao menos uma página executiva
- salvar screenshots do dashboard do Power BI
- adicionar esses arquivos nesta pasta

## Estrutura recomendada nesta pasta

- `case_bonus.pbix`
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

Se o `.pbix` ainda não for criado, o bônus deve ser descrito como:

- `base preparada para Power BI`
- `bônus documentado, mas ainda não materializado visualmente`
