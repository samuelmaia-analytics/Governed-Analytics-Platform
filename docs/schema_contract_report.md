# Relatorio de Contratos de Schema

Este documento registra a validacao dos contratos simples de schema das camadas principais do projeto.

## Resumo

| Dataset | Camada | Checks | Falhas |
| --- | --- | ---: | ---: |
| `fact_orders_enriched` | `curated` | 64 | 0 |
| `fact_orders_dashboard` | `published` | 38 | 0 |
| `olist_customers_dataset` | `standardized` | 9 | 0 |
| `olist_order_items_dataset` | `standardized` | 11 | 0 |
| `olist_orders_dataset` | `standardized` | 12 | 0 |

## Resultado dos Checks

| Dataset | Check | Status | Detalhes |
| --- | --- | --- | --- |
| `fact_orders_enriched` | `missing_columns` | **PASS** | Ausentes: nenhuma |
| `fact_orders_enriched` | `unexpected_columns` | **PASS** | Inesperadas: nenhuma |
| `fact_orders_enriched` | `type__order_id` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__order_item_id` | **PASS** | Esperado=integer | atual=int64 |
| `fact_orders_enriched` | `type__customer_id` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__customer_unique_id` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__product_id` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__seller_id` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__order_status` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__order_purchase_timestamp` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `type__order_approved_at` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `type__shipping_limit_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `type__order_delivered_carrier_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `type__order_delivered_customer_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `type__order_estimated_delivery_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `type__order_date` | **PASS** | Esperado=date_like | atual=object |
| `fact_orders_enriched` | `type__order_year` | **PASS** | Esperado=integer | atual=int32 |
| `fact_orders_enriched` | `type__order_month` | **PASS** | Esperado=integer | atual=int32 |
| `fact_orders_enriched` | `type__purchase_cohort_month` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__customer_first_purchase_timestamp` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `type__cohort_order_month_number` | **PASS** | Esperado=integer | atual=int32 |
| `fact_orders_enriched` | `type__customer_order_sequence` | **PASS** | Esperado=integer | atual=Int64 |
| `fact_orders_enriched` | `type__is_first_order` | **PASS** | Esperado=boolean | atual=boolean |
| `fact_orders_enriched` | `type__delivery_time_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__seller_dispatch_time_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__carrier_delivery_time_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__estimated_delay_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__is_delayed` | **PASS** | Esperado=boolean | atual=bool |
| `fact_orders_enriched` | `type__price` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__freight_value` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__freight_to_price_ratio` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__total_item_value` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__payment_count` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__total_payment_value` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__max_payment_installments` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__payment_type_mode` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__review_count` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__review_score_mean` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__review_score_max` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__review_score_min` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__has_review_comment` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__product_category_name` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__product_category_name_english` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__product_name_lenght` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__product_description_lenght` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__product_photos_qty` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__product_weight_g` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__product_length_cm` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__product_height_cm` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__product_width_cm` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__customer_zip_code_prefix` | **PASS** | Esperado=integer | atual=int64 |
| `fact_orders_enriched` | `type__customer_city` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__customer_state` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__seller_zip_code_prefix` | **PASS** | Esperado=integer | atual=int64 |
| `fact_orders_enriched` | `type__seller_city` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__seller_state` | **PASS** | Esperado=string | atual=object |
| `fact_orders_enriched` | `type__seller_order_count` | **PASS** | Esperado=integer | atual=Int64 |
| `fact_orders_enriched` | `type__seller_avg_delivery_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__seller_delay_rate` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_enriched` | `type__seller_volume_tier` | **PASS** | Esperado=string | atual=string |
| `fact_orders_enriched` | `type__latest_review_creation_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `type__latest_review_answer_timestamp` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_enriched` | `min_rows` | **PASS** | Linhas observadas=112650 | minimo=100001 |
| `fact_orders_enriched` | `primary_key_duplicates` | **PASS** | Chave=['order_id', 'order_item_id', 'product_id', 'seller_id'] | duplicados=0 |
| `fact_orders_dashboard` | `missing_columns` | **PASS** | Ausentes: nenhuma |
| `fact_orders_dashboard` | `unexpected_columns` | **PASS** | Inesperadas: nenhuma |
| `fact_orders_dashboard` | `type__order_id` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__order_item_id` | **PASS** | Esperado=integer | atual=int64 |
| `fact_orders_dashboard` | `type__customer_unique_id` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__order_status` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__order_purchase_timestamp` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_dashboard` | `type__order_delivered_customer_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_dashboard` | `type__order_estimated_delivery_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `fact_orders_dashboard` | `type__order_date` | **PASS** | Esperado=date_like | atual=object |
| `fact_orders_dashboard` | `type__order_year` | **PASS** | Esperado=integer | atual=int32 |
| `fact_orders_dashboard` | `type__order_month` | **PASS** | Esperado=integer | atual=int32 |
| `fact_orders_dashboard` | `type__purchase_cohort_month` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__cohort_order_month_number` | **PASS** | Esperado=integer | atual=int32 |
| `fact_orders_dashboard` | `type__customer_order_sequence` | **PASS** | Esperado=integer | atual=Int64 |
| `fact_orders_dashboard` | `type__is_first_order` | **PASS** | Esperado=boolean | atual=boolean |
| `fact_orders_dashboard` | `type__seller_key` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__seller_volume_tier` | **PASS** | Esperado=string | atual=string |
| `fact_orders_dashboard` | `type__seller_order_count` | **PASS** | Esperado=integer | atual=Int64 |
| `fact_orders_dashboard` | `type__seller_avg_delivery_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__seller_delay_rate` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__delivery_time_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__seller_dispatch_time_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__carrier_delivery_time_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__estimated_delay_days` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__is_delayed` | **PASS** | Esperado=boolean | atual=bool |
| `fact_orders_dashboard` | `type__price` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__freight_value` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__freight_to_price_ratio` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__total_item_value` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__payment_type_mode` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__review_score_mean` | **PASS** | Esperado=float | atual=float64 |
| `fact_orders_dashboard` | `type__product_category_name` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__product_category_name_english` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__customer_state` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `type__seller_state` | **PASS** | Esperado=string | atual=object |
| `fact_orders_dashboard` | `min_rows` | **PASS** | Linhas observadas=112650 | minimo=100001 |
| `fact_orders_dashboard` | `primary_key_duplicates` | **PASS** | Chave=['order_id', 'order_item_id'] | duplicados=0 |
| `olist_customers_dataset` | `missing_columns` | **PASS** | Ausentes: nenhuma |
| `olist_customers_dataset` | `unexpected_columns` | **PASS** | Inesperadas: nenhuma |
| `olist_customers_dataset` | `type__customer_id` | **PASS** | Esperado=string | atual=object |
| `olist_customers_dataset` | `type__customer_unique_id` | **PASS** | Esperado=string | atual=object |
| `olist_customers_dataset` | `type__customer_zip_code_prefix` | **PASS** | Esperado=integer | atual=int64 |
| `olist_customers_dataset` | `type__customer_city` | **PASS** | Esperado=string | atual=object |
| `olist_customers_dataset` | `type__customer_state` | **PASS** | Esperado=string | atual=object |
| `olist_customers_dataset` | `min_rows` | **PASS** | Linhas observadas=99441 | minimo=90000 |
| `olist_customers_dataset` | `primary_key_duplicates` | **PASS** | Chave=['customer_id'] | duplicados=0 |
| `olist_order_items_dataset` | `missing_columns` | **PASS** | Ausentes: nenhuma |
| `olist_order_items_dataset` | `unexpected_columns` | **PASS** | Inesperadas: nenhuma |
| `olist_order_items_dataset` | `type__order_id` | **PASS** | Esperado=string | atual=object |
| `olist_order_items_dataset` | `type__order_item_id` | **PASS** | Esperado=integer | atual=int64 |
| `olist_order_items_dataset` | `type__product_id` | **PASS** | Esperado=string | atual=object |
| `olist_order_items_dataset` | `type__seller_id` | **PASS** | Esperado=string | atual=object |
| `olist_order_items_dataset` | `type__shipping_limit_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `olist_order_items_dataset` | `type__price` | **PASS** | Esperado=float | atual=float64 |
| `olist_order_items_dataset` | `type__freight_value` | **PASS** | Esperado=float | atual=float64 |
| `olist_order_items_dataset` | `min_rows` | **PASS** | Linhas observadas=112650 | minimo=100000 |
| `olist_order_items_dataset` | `primary_key_duplicates` | **PASS** | Chave=['order_id', 'order_item_id', 'product_id', 'seller_id'] | duplicados=0 |
| `olist_orders_dataset` | `missing_columns` | **PASS** | Ausentes: nenhuma |
| `olist_orders_dataset` | `unexpected_columns` | **PASS** | Inesperadas: nenhuma |
| `olist_orders_dataset` | `type__order_id` | **PASS** | Esperado=string | atual=object |
| `olist_orders_dataset` | `type__customer_id` | **PASS** | Esperado=string | atual=object |
| `olist_orders_dataset` | `type__order_status` | **PASS** | Esperado=string | atual=object |
| `olist_orders_dataset` | `type__order_purchase_timestamp` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `olist_orders_dataset` | `type__order_approved_at` | **PASS** | Esperado=string | atual=object |
| `olist_orders_dataset` | `type__order_delivered_carrier_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `olist_orders_dataset` | `type__order_delivered_customer_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `olist_orders_dataset` | `type__order_estimated_delivery_date` | **PASS** | Esperado=datetime | atual=datetime64[ns] |
| `olist_orders_dataset` | `min_rows` | **PASS** | Linhas observadas=99441 | minimo=90000 |
| `olist_orders_dataset` | `primary_key_duplicates` | **PASS** | Chave=['order_id'] | duplicados=0 |