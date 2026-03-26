# Power BI

Esta pasta reúne a trilha complementar de BI externo do projeto.

## Papel do bônus

O material de Power BI amplia o consumo analítico do case. Ele não substitui o dashboard principal em Streamlit, mas demonstra reutilização da mesma base em um modelo estrela simples.

## Conteúdo

- `README_powerbi.md`: guia do dashboard
- `evidencia_query.md`: evidências da query principal
- `INSIGHTS_EXECUTIVOS.md`: leitura gerencial
- `checklist_entrega.md`: conferência final
- `delivery_plan.md`: plano operacional
- `dashboard_overview.pbix`: arquivo do relatório
- `dashboard_overview.png` e `dashboard_drilldown.png`: capturas do dashboard

## Bases importadas

- `fact_sales_power_bi.csv`
- `dim_date.csv`
- `dim_product.csv`
- `dim_customer.csv`
- `dim_seller.csv`
- `dim_payment.csv`
- `dim_order_status.csv`

## Observação importante

Os CSVs exportados para Power BI usam separador `;` e encoding `utf-8-sig`.

## Referências

- documentação do bônus: [../docs/bi_bonus.md](../docs/bi_bonus.md)
- guia do dashboard: [README_powerbi.md](README_powerbi.md)
- evidência SQL: [evidencia_query.md](evidencia_query.md)
