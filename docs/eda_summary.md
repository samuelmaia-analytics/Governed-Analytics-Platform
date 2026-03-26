# Resumo de EDA


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`

Resumo exploratório inicial dos CSVs em `data/raw/landing/olist/`, com tabelas padronizadas promovidas para `data/standardized/olist/`.

## Visão Geral

| Tabela | Linhas | Colunas | IDs | Datas | Numéricas | Categóricas | Possíveis chaves | Linhas duplicadas |
| --- | ---: | ---: | --- | --- | --- | --- | --- | ---: |
| olist_customers_dataset | 99441 | 5 | customer_id, customer_unique_id | - | customer_zip_code_prefix | customer_city, customer_id, customer_state, customer_unique_id | customer_id | 0 |
| olist_geolocation_dataset | 1000163 | 5 | - | - | geolocation_lat, geolocation_lng, geolocation_zip_code_prefix | geolocation_city, geolocation_state | - | 390005 |
| olist_order_items_dataset | 112650 | 7 | order_id, order_item_id, product_id, seller_id | shipping_limit_date | freight_value, order_item_id, price | order_id, product_id, seller_id | - | 0 |
| olist_order_payments_dataset | 103886 | 5 | order_id | - | payment_installments, payment_sequential, payment_value | order_id, payment_type | - | 0 |
| olist_order_reviews_dataset | 99224 | 7 | order_id, review_id | review_answer_timestamp, review_creation_date | review_score | order_id, review_comment_message, review_comment_title, review_id | - | 0 |
| olist_orders_dataset | 99441 | 8 | customer_id, order_id | order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, order_purchase_timestamp | - | customer_id, order_approved_at, order_id, order_status | customer_id, order_id | 0 |
| olist_products_dataset | 32951 | 9 | product_id | - | product_description_lenght, product_height_cm, product_length_cm, product_name_lenght, product_photos_qty, product_weight_g, product_width_cm | product_category_name, product_id | product_id | 0 |
| olist_sellers_dataset | 3095 | 4 | seller_id | - | seller_zip_code_prefix | seller_city, seller_id, seller_state | seller_id | 0 |
| product_category_name_translation | 71 | 2 | - | - | - | product_category_name, product_category_name_english | - | 0 |

## Detalhes por Tabela

### olist_customers_dataset

- Arquivo: `olist_customers_dataset.csv`
- Encoding: `utf-8`
- Shape: `99441 x 5`
- Colunas ID: `customer_id, customer_unique_id`
- Colunas de data: `nenhuma`
- Colunas numéricas: `customer_zip_code_prefix`
- Colunas categóricas: `customer_city, customer_id, customer_state, customer_unique_id`
- Possíveis chaves: `customer_id`
- Linhas duplicadas: `0` (0.00%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| - | 0 | 0.00% |

### olist_geolocation_dataset

- Arquivo: `olist_geolocation_dataset.csv`
- Encoding: `utf-8`
- Shape: `1000163 x 5`
- Colunas ID: `nenhuma`
- Colunas de data: `nenhuma`
- Colunas numéricas: `geolocation_lat, geolocation_lng, geolocation_zip_code_prefix`
- Colunas categóricas: `geolocation_city, geolocation_state`
- Possíveis chaves: `nenhuma`
- Linhas duplicadas: `390005` (38.99%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| - | 0 | 0.00% |

### olist_order_items_dataset

- Arquivo: `olist_order_items_dataset.csv`
- Encoding: `utf-8`
- Shape: `112650 x 7`
- Colunas ID: `order_id, order_item_id, product_id, seller_id`
- Colunas de data: `shipping_limit_date`
- Colunas numéricas: `freight_value, order_item_id, price`
- Colunas categóricas: `order_id, product_id, seller_id`
- Possíveis chaves: `nenhuma`
- Linhas duplicadas: `0` (0.00%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| - | 0 | 0.00% |

### olist_order_payments_dataset

- Arquivo: `olist_order_payments_dataset.csv`
- Encoding: `utf-8`
- Shape: `103886 x 5`
- Colunas ID: `order_id`
- Colunas de data: `nenhuma`
- Colunas numéricas: `payment_installments, payment_sequential, payment_value`
- Colunas categóricas: `order_id, payment_type`
- Possíveis chaves: `nenhuma`
- Linhas duplicadas: `0` (0.00%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| - | 0 | 0.00% |

### olist_order_reviews_dataset

- Arquivo: `olist_order_reviews_dataset.csv`
- Encoding: `utf-8`
- Shape: `99224 x 7`
- Colunas ID: `order_id, review_id`
- Colunas de data: `review_answer_timestamp, review_creation_date`
- Colunas numéricas: `review_score`
- Colunas categóricas: `order_id, review_comment_message, review_comment_title, review_id`
- Possíveis chaves: `nenhuma`
- Linhas duplicadas: `0` (0.00%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| `review_comment_title` | 87656 | 88.34% |
| `review_comment_message` | 58247 | 58.70% |

### olist_orders_dataset

- Arquivo: `olist_orders_dataset.csv`
- Encoding: `utf-8`
- Shape: `99441 x 8`
- Colunas ID: `customer_id, order_id`
- Colunas de data: `order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, order_purchase_timestamp`
- Colunas numéricas: `nenhuma`
- Colunas categóricas: `customer_id, order_approved_at, order_id, order_status`
- Possíveis chaves: `customer_id, order_id`
- Linhas duplicadas: `0` (0.00%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| `order_delivered_customer_date` | 2965 | 2.98% |
| `order_delivered_carrier_date` | 1783 | 1.79% |
| `order_approved_at` | 160 | 0.16% |

### olist_products_dataset

- Arquivo: `olist_products_dataset.csv`
- Encoding: `utf-8`
- Shape: `32951 x 9`
- Colunas ID: `product_id`
- Colunas de data: `nenhuma`
- Colunas numéricas: `product_description_lenght, product_height_cm, product_length_cm, product_name_lenght, product_photos_qty, product_weight_g, product_width_cm`
- Colunas categóricas: `product_category_name, product_id`
- Possíveis chaves: `product_id`
- Linhas duplicadas: `0` (0.00%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| `product_category_name` | 610 | 1.85% |
| `product_description_lenght` | 610 | 1.85% |
| `product_name_lenght` | 610 | 1.85% |
| `product_photos_qty` | 610 | 1.85% |
| `product_height_cm` | 2 | 0.01% |
| `product_length_cm` | 2 | 0.01% |
| `product_weight_g` | 2 | 0.01% |
| `product_width_cm` | 2 | 0.01% |

### olist_sellers_dataset

- Arquivo: `olist_sellers_dataset.csv`
- Encoding: `utf-8`
- Shape: `3095 x 4`
- Colunas ID: `seller_id`
- Colunas de data: `nenhuma`
- Colunas numéricas: `seller_zip_code_prefix`
- Colunas categóricas: `seller_city, seller_id, seller_state`
- Possíveis chaves: `seller_id`
- Linhas duplicadas: `0` (0.00%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| - | 0 | 0.00% |

### product_category_name_translation

- Arquivo: `product_category_name_translation.csv`
- Encoding: `utf-8`
- Shape: `71 x 2`
- Colunas ID: `nenhuma`
- Colunas de data: `nenhuma`
- Colunas numéricas: `nenhuma`
- Colunas categóricas: `product_category_name, product_category_name_english`
- Possíveis chaves: `nenhuma`
- Linhas duplicadas: `0` (0.00%)

#### Top colunas com nulos

| Coluna | Nulos | Percentual |
| --- | ---: | ---: |
| - | 0 | 0.00% |

## Artefatos Gerados

- `data/standardized/olist/*.parquet`
- `data/staging/profiling/profiling_overview.csv`
- `data/staging/profiling/all_columns_profile.csv`
- `data/staging/profiling/all_nulls_profile.csv`
- `data/staging/profiling/all_possible_keys.csv`
- `data/staging/profiling/all_duplicate_profile.csv`


