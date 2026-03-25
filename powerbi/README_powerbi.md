# Dashboard Power BI | SAMUEL_MAIA_DDF_TECH_032026

## Objetivo do dashboard

Apresentar uma visão executiva e analítica do desempenho do e-commerce Olist, combinando indicadores de receita, volume, experiência do cliente, eficiência operacional e recortes por tempo, categoria, status e geografia.

O dashboard foi desenhado para sustentar uma conversa de negócio, mas com base técnica rastreável e compatível com o modelo analítico do projeto.

## Contexto do dataset

O projeto utiliza a base Olist e consolida os dados em uma camada analítica principal derivada de `fact_orders_enriched`.

Para consumo no Power BI, essa camada foi exportada para um modelo estrela simples, com uma fato de vendas e dimensões auxiliares de data, produto, pagamento, status, cliente e seller.

## Modelo de dados

Estrutura principal:

- fato:
  - `fact_sales_power_bi.csv`

- dimensões:
  - `dim_date.csv`
  - `dim_product.csv`
  - `dim_payment.csv`
  - `dim_order_status.csv`
  - `dim_customer.csv`
  - `dim_seller.csv`

Relacionamentos esperados:

- `fact_sales_power_bi[date_key]` -> `dim_date[date_key]`
- `fact_sales_power_bi[product_key]` -> `dim_product[product_key]`
- `fact_sales_power_bi[payment_key]` -> `dim_payment[payment_key]`
- `fact_sales_power_bi[order_status_key]` -> `dim_order_status[order_status_key]`
- `fact_sales_power_bi[customer_key]` -> `dim_customer[customer_key]`
- `fact_sales_power_bi[seller_key]` -> `dim_seller[seller_key]`

## Principais KPIs

- Receita Total
- Total de Pedidos
- Ticket Médio
- Review Médio
- % Pedidos em Atraso

## Páginas e visuais principais

Estrutura executiva recomendada:

- cards de KPIs
- Evolução da Receita no Tempo
- Top 10 Categorias por Receita
- Distribuição dos Pedidos por Status
- análise por meio de pagamento
- análise por estado
- tabela de detalhamento por categoria ou geografia

## Principais insights de negócio

O dashboard foi estruturado para responder rapidamente:

- como a receita evolui ao longo do tempo
- quais categorias concentram maior geração de valor
- quais estados combinam volume relevante com pior atraso
- como os status dos pedidos impactam a leitura operacional
- como a experiência do cliente se conecta com receita e entrega

## Instruções de uso

1. Abrir o arquivo `.pbix` atual do projeto.
2. Validar os relacionamentos do modelo estrela.
3. Conferir se os cards principais estão coerentes.
4. Aplicar filtros por ano, categoria, status, pagamento e estado.
5. Validar se os visuais respondem corretamente ao cruzamento dos filtros.

Arquivos-base do modelo:

- [fact_sales_power_bi.csv](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\processed\bi_exports\fact_sales_power_bi.csv)
- [dim_date.csv](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\processed\bi_exports\dim_date.csv)
- [dim_product.csv](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\processed\bi_exports\dim_product.csv)
- [dim_payment.csv](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\processed\bi_exports\dim_payment.csv)
- [dim_order_status.csv](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\processed\bi_exports\dim_order_status.csv)
- [dim_customer.csv](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\processed\bi_exports\dim_customer.csv)
- [dim_seller.csv](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\data\processed\bi_exports\dim_seller.csv)

Artefatos já encontrados no projeto:

- arquivo Power BI atual: [dashboard_overview.pbix](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\dashboard_overview.pbix)
- print executivo atual: [dashboard_overview.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\dashboard_overview.png)
- evidência SQL principal: [evidencia_query.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\evidencia_query.md)
- print do resultado SQL: [query_principal_resultado.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\powerbi\query_principal_resultado.png)

## Onde inserir imagem ou print final do dashboard

Marcadores recomendados:

- `powerbi/dashboard_overview.png`
- `powerbi/dashboard_drilldown.png`

Status atual:

- `dashboard_overview.png`: disponível
- `dashboard_drilldown.png`: disponível
