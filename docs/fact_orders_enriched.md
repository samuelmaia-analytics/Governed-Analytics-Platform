# fact_orders_enriched

Tabela analítica principal derivada do dataset Olist com granularidade por item de pedido.

## Resumo

- Total de registros: **112,650**
- Total de colunas: **60**

## Regras de Negócio

- A tabela base parte de `order_items`, preservando uma linha por item de pedido.
- `orders`, `customers`, `products`, `sellers` e `translation` entram por joins dimensionais `many_to_one`.
- `payments` e `reviews` são agregados por `order_id` antes do join para evitar duplicação artificial de itens.
- `total_item_value` é calculado como `price + freight_value` no nível do item.
- `delivery_time_days` mede o tempo entre compra e entrega ao cliente.
- `seller_dispatch_time_days` mede o tempo entre aprovacao e despacho para a transportadora.
- `carrier_delivery_time_days` mede o trecho transportadora -> cliente quando a origem traz os timestamps.
- `estimated_delay_days` mede a diferença entre a entrega real e a data estimada; permanece nulo quando não há entrega registrada.
- `is_delayed` sinaliza pedidos entregues após a data estimada.
- `purchase_cohort_month`, `customer_order_sequence` e `cohort_order_month_number` habilitam analise de cohort e recorrencia.
- `seller_order_count`, `seller_avg_delivery_days`, `seller_delay_rate` e `seller_volume_tier` habilitam recortes semanticos de seller.
- `freight_to_price_ratio` qualifica o peso relativo do frete sobre o item vendido.
- Registros com chaves essenciais ausentes, valores monetários negativos ou entrega anterior à compra são removidos.

## Cobertura de Enriquecimento

| Atributo | Percentual ausente |
| --- | ---: |
| `customer_unique_id` | 0.00% |
| `customer_state` | 0.00% |
| `seller_state` | 0.00% |
| `payment_type_mode` | 0.00% |
| `product_category_name` | 1.42% |
| `product_category_name_english` | 1.44% |

## Reconciliação Financeira em Nível de Pedido

- Pedidos reconciliados: **98,666**
- Gap absoluto médio entre `sum(total_item_value)` e `total_payment_value`: **0.0346**
- Gap absoluto máximo observado: **182.8100**
- Percentual de pedidos com gap acima de R$ 1,00: **0.25%**

## Decisão de Granularidade

- A granularidade escolhida é `order_id + order_item_id + product_id + seller_id`.
- Essa decisão preserva a análise por item vendido, seller e produto, sem perder contexto de pedido, cliente, pagamento e review.

## Principais Limitações

- `payments` e `reviews` são resumidos ao nível do pedido, portanto distribuições internas por item não existem na fonte final.
- Algumas colunas de data do dataset original possuem ausências; nesses casos, as métricas derivadas podem ficar nulas ou simplificadas.
- A regra de inconsistência é propositalmente conservadora e remove apenas anomalias óbvias.
- O campo `order_approved_at` pode permanecer nulo ou texto convertido para `NaT` quando a origem estiver incompleta.
