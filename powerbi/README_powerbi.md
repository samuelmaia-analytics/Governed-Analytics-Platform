# Dashboard Power BI | Governed Analytics Platform

[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live-red?logo=streamlit)](https://governed-analytics-platform.streamlit.app/)
[![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811?logo=powerbi&logoColor=black)](https://app.powerbi.com/links/Xto6lIUiRF?ctid=b1b9d429-7862-4440-a25b-6ca19f868f47&pbi_source=linkShare)


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/Governed-Analytics-Platform`
- App Streamlit: `https://governed-analytics-platform.streamlit.app/`
- Dashboard Power BI: `https://app.powerbi.com/links/Xto6lIUiRF?ctid=b1b9d429-7862-4440-a25b-6ca19f868f47&pbi_source=linkShare`

## Objetivo do dashboard

Apresentar uma visão executiva e analítica do desempenho do e-commerce Olist, combinando indicadores de receita, volume, experiência do cliente, eficiência operacional e recortes por tempo, categoria, status e geografia.

O dashboard foi desenhado para sustentar uma conversa de negócio com base técnica rastreável e compatível com o modelo analítico do projeto.

## Contexto do dataset

O projeto utiliza a base Olist e consolida os dados em uma camada publicada governada em `fact_orders_dashboard`.

Para consumo no Power BI, essa camada publicada foi exportada para um modelo estrela simples, com uma fato de vendas e dimensões auxiliares compatíveis com a fronteira de exposição executiva: data, categoria, pagamento, status, cliente pseudonimizado e seller pseudonimizado.

## Modelo de dados

Estrutura principal:

- fato:
  - `fact_sales_power_bi.csv`

- dimensões:
  - `dim_date.csv`
  - `dim_category.csv`
  - `dim_payment.csv`
  - `dim_order_status.csv`
  - `dim_customer.csv`
  - `dim_seller.csv`

Relacionamentos esperados:

- `fact_sales_power_bi[date_key]` -> `dim_date[date_key]`
- `fact_sales_power_bi[category_key]` -> `dim_category[category_key]`
- `fact_sales_power_bi[payment_key]` -> `dim_payment[payment_key]`
- `fact_sales_power_bi[order_status_key]` -> `dim_order_status[order_status_key]`
- `fact_sales_power_bi[customer_key]` -> `dim_customer[customer_key]`
- `fact_sales_power_bi[seller_key]` -> `dim_seller[seller_key]`

Observações de importação:

- separador CSV: `;`
- encoding: `utf-8-sig`
- fato e dimensões são derivados da camada publicada `fact_orders_dashboard`
- o modelo evita reintroduzir chaves brutas ou atributos detalhados removidos na publicação governada

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
- como a experiência do cliente se conecta com receita e desempenho operacional

## Instruções de uso

1. Abrir o arquivo `.pbix` atual do projeto.
2. Importar ou atualizar os CSVs usando separador `;`.
3. Validar os relacionamentos do modelo estrela.
4. Conferir se os cards principais estão coerentes.
5. Aplicar filtros por ano, categoria, status, pagamento e estado.
6. Validar se os visuais respondem corretamente ao cruzamento dos filtros.

Arquivos-base do modelo:

- [fact_sales_power_bi.csv](../data/processed/bi_exports/fact_sales_power_bi.csv)
- [dim_date.csv](../data/processed/bi_exports/dim_date.csv)
- [dim_category.csv](../data/processed/bi_exports/dim_category.csv)
- [dim_payment.csv](../data/processed/bi_exports/dim_payment.csv)
- [dim_order_status.csv](../data/processed/bi_exports/dim_order_status.csv)
- [dim_customer.csv](../data/processed/bi_exports/dim_customer.csv)
- [dim_seller.csv](../data/processed/bi_exports/dim_seller.csv)

Artefatos já encontrados no projeto:

- arquivo Power BI atual: [dashboard_overview.pbix](./dashboard_overview.pbix)
- print executivo atual: [dashboard_overview.png](./dashboard_overview.png)
- evidência SQL principal: [evidencia_query.md](./evidencia_query.md)
- print do resultado SQL: [query_principal_resultado.png](./query_principal_resultado.png)

## Onde inserir imagem ou print final do dashboard

Marcadores recomendados:

- `powerbi/dashboard_overview.png`
- `powerbi/dashboard_drilldown.png`

Status atual:

- `dashboard_overview.png`: disponível
- `dashboard_drilldown.png`: disponível

