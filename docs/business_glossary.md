# Business Glossary

## Objective

This glossary standardizes the business language of the project so that Streamlit, Power BI, SQL and documentation use the same definitions.

## Business terms

| Term | Business Meaning | Analytical Definition | Notes |
| --- | --- | --- | --- |
| Receita | Monetary value generated in the sale flow. | `sum(total_item_value)` | Includes item price and freight in this project. |
| Pedido | A customer purchase event. | `order_id` distinct | Executive counts should use distinct orders, not item rows. |
| Item de pedido | Sold line within an order. | `order_id + order_item_id` | Base grain of the published dashboard layer. |
| Cliente | Unique buyer entity in the published layer. | `customer_unique_id` pseudonymized | Used for distinct customer and recurrence analysis. |
| Seller | Merchant responsible for the sold item. | `seller_key` pseudonymized | Governed exposure avoids raw seller identifiers. |
| Ticket médio | Average revenue per order. | `receita / pedidos` | Must be computed at order level. |
| Frete médio por item | Average freight paid at item level. | `avg(freight_value)` | Useful for operational and margin pressure reading. |
| Pedido atrasado | Delivered order later than estimated. | `is_delayed = true` | Depends on actual and estimated delivery dates being present. |
| Taxa de atraso | Share of delayed delivered population. | `avg(is_delayed)` | Prefer comparison on delivered population. |
| Prazo médio | Average elapsed time from purchase to delivery. | `avg(delivery_time_days)` | Delivery-only measure. |
| Cohort de compra | Group of customers by first purchase month. | `purchase_cohort_month` | Used for retention and recurrence analysis. |
| Recompra | Repeat purchasing behavior. | customer with `customer_order_sequence > 1` | Better served from a future semantic mart. |
| Retenção | Customer continuity after cohort start. | returning customers over cohort base | Should be tracked by relative cohort month. |
| SLA logístico | Expected logistics performance level. | operationally proxied by delay rate and delivery time | This project does not model contractual SLA by partner. |
| Seller ativo | Seller with transaction activity in the selected scope. | distinct `seller_key` in scope | Activity-based, not registry-based. |
| Camada publicada | Governed exposure layer used by executive consumers. | `fact_orders_dashboard` and semantic published assets | Official boundary for recurring consumption. |
| Camada interna | Internal analytical layer for engineering and audit. | `fact_orders_enriched` | Not the default exposure contract. |

## Standard interpretation rules

- When the term "receita" is used in executive outputs, it means gross revenue with freight included unless stated otherwise.
- When the term "pedido" is used, it means a distinct order and should not be confused with item-level records.
- When the term "cliente" is used in the published layer, it refers to the pseudonymized customer key, not a raw transactional identifier.
- When the term "seller" is used in executive outputs, it refers to the pseudonymized seller key.
- When a metric depends on delivered orders only, that restriction should be explicit in the chart, tooltip or documentation.

## Recommended labeling standard

- Technical ids: English, snake_case
- Executive labels: Portuguese, concise and business-oriented
- Metric explanations: plain business language plus analytical caveat when necessary

## Terms that should not remain ambiguous

- `receita` versus `valor do item`
- `pedido` versus `item`
- `cliente` versus `customer_id`
- `seller` versus raw `seller_id`
- `atraso` versus undelivered order
- `ticket médio` versus item average value

## Governance note

This glossary should evolve together with the metric catalog. If a business definition changes, both artifacts should be updated in the same change set.
