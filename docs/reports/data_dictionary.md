# Data Dictionary

- Generated at: **2026-05-11 17:35:32 UTC**
- Total rows: **112650**
- Total columns: **34**

## Column Dictionary

| column_name | dtype | null_pct | distinct_values | lgpd_classification |
| --- | --- | --- | --- | --- |
| order_id | object | 0.0 | 98666 | personal_data |
| order_item_id | int64 | 0.0 | 21 | non_personal |
| customer_unique_id | object | 0.0 | 95420 | personal_data |
| order_status | object | 0.0 | 7 | non_personal |
| order_purchase_timestamp | object | 0.0 | 98112 | non_personal |
| order_delivered_customer_date | object | 2.18 | 95665 | non_personal |
| order_estimated_delivery_date | object | 0.0 | 450 | non_personal |
| order_date | object | 0.0 | 616 | non_personal |
| order_year | int64 | 0.0 | 3 | non_personal |
| order_month | int64 | 0.0 | 12 | non_personal |
| purchase_cohort_month | object | 0.0 | 24 | non_personal |
| cohort_order_month_number | int64 | 0.0 | 20 | non_personal |
| customer_order_sequence | int64 | 0.0 | 16 | non_personal |
| is_first_order | bool | 0.0 | 2 | non_personal |
| seller_key | object | 0.0 | 3095 | personal_data |
| seller_volume_tier | object | 0.0 | 4 | non_personal |
| seller_order_count | int64 | 0.0 | 251 | non_personal |
| seller_avg_delivery_days | float64 | 0.18 | 2971 | personal_data |
| seller_delay_rate | float64 | 0.0 | 453 | personal_data |
| delivery_time_days | float64 | 2.18 | 93810 | personal_data |
| seller_dispatch_time_days | float64 | 1.07 | 87498 | personal_data |
| carrier_delivery_time_days | float64 | 2.18 | 92240 | personal_data |
| estimated_delay_days | float64 | 2.18 | 91916 | personal_data |
| is_delayed | bool | 0.0 | 2 | non_personal |
| price | float64 | 0.0 | 5968 | non_personal |
| freight_value | float64 | 0.0 | 6999 | non_personal |
| freight_to_price_ratio | float64 | 0.0 | 46554 | personal_data |
| total_item_value | float64 | 0.0 | 27029 | personal_data |
| payment_type_mode | object | 0.0 | 5 | non_personal |
| review_score_mean | float64 | 0.84 | 12 | non_personal |
| product_category_name | object | 1.42 | 74 | personal_data |
| product_category_name_english | object | 1.44 | 72 | personal_data |
| customer_state | object | 0.0 | 27 | indirect_identifier |
| seller_state | object | 0.0 | 23 | indirect_identifier |