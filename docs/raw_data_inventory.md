# Inventário de Dados Brutos

Inventário gerado automaticamente a partir dos CSVs do dataset Olist em `data/raw/landing/olist/`.

Total de arquivos analisados: **9**

## olist_customers_dataset.csv

- Caminho: `raw/landing/olist/olist_customers_dataset.csv`
- Shape: `99441 x 5`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `nenhuma`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `customer_id` | `object` |
| `customer_unique_id` | `object` |
| `customer_zip_code_prefix` | `int64` |
| `customer_city` | `object` |
| `customer_state` | `object` |

## olist_geolocation_dataset.csv

- Caminho: `raw/landing/olist/olist_geolocation_dataset.csv`
- Shape: `1000163 x 5`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `nenhuma`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `geolocation_zip_code_prefix` | `int64` |
| `geolocation_lat` | `float64` |
| `geolocation_lng` | `float64` |
| `geolocation_city` | `object` |
| `geolocation_state` | `object` |

## olist_order_items_dataset.csv

- Caminho: `raw/landing/olist/olist_order_items_dataset.csv`
- Shape: `112650 x 7`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `shipping_limit_date`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `order_id` | `object` |
| `order_item_id` | `int64` |
| `product_id` | `object` |
| `seller_id` | `object` |
| `shipping_limit_date` | `datetime64[ns]` |
| `price` | `float64` |
| `freight_value` | `float64` |

## olist_order_payments_dataset.csv

- Caminho: `raw/landing/olist/olist_order_payments_dataset.csv`
- Shape: `103886 x 5`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `nenhuma`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `order_id` | `object` |
| `payment_sequential` | `int64` |
| `payment_type` | `object` |
| `payment_installments` | `int64` |
| `payment_value` | `float64` |

## olist_order_reviews_dataset.csv

- Caminho: `raw/landing/olist/olist_order_reviews_dataset.csv`
- Shape: `99224 x 7`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `review_creation_date, review_answer_timestamp`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `review_id` | `object` |
| `order_id` | `object` |
| `review_score` | `int64` |
| `review_comment_title` | `object` |
| `review_comment_message` | `object` |
| `review_creation_date` | `datetime64[ns]` |
| `review_answer_timestamp` | `datetime64[ns]` |

## olist_orders_dataset.csv

- Caminho: `raw/landing/olist/olist_orders_dataset.csv`
- Shape: `99441 x 8`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `order_purchase_timestamp, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `order_id` | `object` |
| `customer_id` | `object` |
| `order_status` | `object` |
| `order_purchase_timestamp` | `datetime64[ns]` |
| `order_approved_at` | `object` |
| `order_delivered_carrier_date` | `datetime64[ns]` |
| `order_delivered_customer_date` | `datetime64[ns]` |
| `order_estimated_delivery_date` | `datetime64[ns]` |

## olist_products_dataset.csv

- Caminho: `raw/landing/olist/olist_products_dataset.csv`
- Shape: `32951 x 9`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `nenhuma`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `product_id` | `object` |
| `product_category_name` | `object` |
| `product_name_lenght` | `float64` |
| `product_description_lenght` | `float64` |
| `product_photos_qty` | `float64` |
| `product_weight_g` | `float64` |
| `product_length_cm` | `float64` |
| `product_height_cm` | `float64` |
| `product_width_cm` | `float64` |

## olist_sellers_dataset.csv

- Caminho: `raw/landing/olist/olist_sellers_dataset.csv`
- Shape: `3095 x 4`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `nenhuma`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `seller_id` | `object` |
| `seller_zip_code_prefix` | `int64` |
| `seller_city` | `object` |
| `seller_state` | `object` |

## product_category_name_translation.csv

- Caminho: `raw/landing/olist/product_category_name_translation.csv`
- Shape: `71 x 2`
- Encoding utilizado: `utf-8`
- Colunas com parsing de data: `nenhuma`

### Colunas

| Coluna | Tipo |
| --- | --- |
| `product_category_name` | `object` |
| `product_category_name_english` | `object` |


