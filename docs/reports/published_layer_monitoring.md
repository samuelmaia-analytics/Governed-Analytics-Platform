# Monitoramento da Camada Published

Relatorio recorrente de freshness e qualidade da camada `fact_orders_dashboard`.

## Resumo

- Checks executados: **12**
- Checks aprovados: **12**
- Checks reprovados: **0**

## Resultado dos Checks

| Check | Status | Valor | Threshold | Severidade |
| --- | --- | ---: | ---: | --- |
| `published_file_freshness_hours` | **PASS** | 0.0 | 36.0 | high |
| `published_expected_schema` | **PASS** | 0.0 | 0.0 | high |
| `published_primary_key_duplicates` | **PASS** | 0.0 | 0.0 | high |
| `published_min_rows` | **PASS** | 112650.0 | 100001.0 | high |
| `published_critical_nulls__order_id` | **PASS** | 0.0 | 0.0 | high |
| `published_critical_nulls__order_item_id` | **PASS** | 0.0 | 0.0 | high |
| `published_critical_nulls__seller_key` | **PASS** | 0.0 | 0.0 | high |
| `published_critical_nulls__order_purchase_timestamp` | **PASS** | 0.0 | 0.0 | high |
| `published_critical_nulls__price` | **PASS** | 0.0 | 0.0 | high |
| `published_critical_nulls__freight_value` | **PASS** | 0.0 | 0.0 | high |
| `published_missing_pct__purchase_cohort_month` | **PASS** | 0.0 | 0.0 | medium |
| `published_missing_pct__seller_delay_rate` | **PASS** | 0.0 | 1.0 | medium |

## Alertas

- Nenhum alerta aberto na execucao atual.

