# Relatório de Qualidade de Dados


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/olist-governed-analytics-platform`
- Dashboard Streamlit: `https://olist-governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Relatório de validação da tabela `fact_orders_enriched`.

## Resumo

- Total de registros avaliados: **112,650**
- Total de colunas avaliadas no dataset: **48**
- Total de checks executados: **25**
- Checks aprovados: **24**
- Checks reprovados: **1**

## Resultado dos Checks

| Check | Status | Valor | Threshold | Severidade |
| --- | --- | ---: | ---: | --- |
| `expected_schema` | **PASS** | 0.0 | 0.0 | high |
| `critical_nulls__order_id` | **PASS** | 0.0 | 0.0 | high |
| `critical_nulls__order_item_id` | **PASS** | 0.0 | 0.0 | high |
| `critical_nulls__customer_id` | **PASS** | 0.0 | 0.0 | high |
| `critical_nulls__product_id` | **PASS** | 0.0 | 0.0 | high |
| `critical_nulls__seller_id` | **PASS** | 0.0 | 0.0 | high |
| `critical_nulls__order_purchase_timestamp` | **PASS** | 0.0 | 0.0 | high |
| `critical_nulls__price` | **PASS** | 0.0 | 0.0 | high |
| `critical_nulls__freight_value` | **PASS** | 0.0 | 0.0 | high |
| `granularity_duplicates` | **PASS** | 0.0 | 0.0 | high |
| `negative_price_values` | **PASS** | 0.0 | 0.0 | high |
| `negative_freight_values` | **PASS** | 0.0 | 0.0 | high |
| `temporal_coherence__approval_before_purchase` | **PASS** | 0.0 | 0.0 | medium |
| `temporal_coherence__delivery_before_purchase` | **PASS** | 0.0 | 0.0 | high |
| `temporal_coherence__delivery_before_approval` | **FAIL** | 69.0 | 0.0 | medium |
| `review_score_missing_pct` | **PASS** | 0.84 | 35.0 | medium |
| `category_missing_pct` | **PASS** | 1.42 | 5.0 | medium |
| `undelivered_orders_pct` | **PASS** | 2.18 | 5.0 | medium |
| `delay_null_consistency` | **PASS** | 0.0 | 0.0 | high |
| `dimension_join_missing_pct__customer_unique_id` | **PASS** | 0.0 | 1.0 | medium |
| `dimension_join_missing_pct__customer_state` | **PASS** | 0.0 | 1.0 | medium |
| `dimension_join_missing_pct__seller_state` | **PASS** | 0.0 | 1.0 | medium |
| `dimension_join_missing_pct__payment_type_mode` | **PASS** | 0.0 | 1.0 | medium |
| `payment_reconciliation_gap_over_1_real_pct` | **PASS** | 0.25 | 5.0 | medium |
| `record_volume_above_100k` | **PASS** | 112650.0 | 100001.0 | high |

## Observações

- `temporal_coherence__delivery_before_approval`: Pedidos entregues antes do timestamp de aprovação. Valor observado=69.0.

## Nota sobre a Falha Residual

- A falha em `delivery_before_approval` indica uma inconsistência pontual presente nos dados de origem.
- O pipeline atual preserva esse comportamento para manter rastreabilidade sobre a fonte, em vez de mascarar o problema com correções arbitrárias.
- Como o volume afetado é baixo frente ao total da base, o ponto foi mantido como alerta de qualidade e não como bloqueio da camada analítica.

## Regras Avaliadas

- Presença do schema mínimo esperado para consumo analítico.
- Ausência de nulos em colunas críticas de identificação e valor.
- Ausência de duplicidade na granularidade `order_id + order_item_id + product_id + seller_id`.
- Ausência de valores negativos em preço e frete.
- Coerência temporal entre compra, aprovação e entrega.
- Percentual de ausência de review score dentro do limite aceitável.
- Percentual de ausência de categoria dentro do limite aceitável.
- Percentual de pedidos sem entrega final dentro do limite aceitável.
- Consistência entre ausência de entrega e ausência de `estimated_delay_days`.
- Cobertura mínima dos principais atributos enriquecidos da camada dimensional.
- Reconciliação financeira entre valor do pedido na grain analítica e total pago por pedido.
- Volume total acima de 100.000 registros.



