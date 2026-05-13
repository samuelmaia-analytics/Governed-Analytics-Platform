# LGPD Controls

- Generated at: **2026-05-11 17:35:32 UTC**
- Risk score: **100 / 100**
- Risk level: **high**

## Dataset Summary

- Total rows: **112650**
- Total columns: **34**
- Risk summary: Dataset with 13 personal, 0 sensitive and 2 indirect identifier columns over 112650 rows.

## LGPD Classification by Column

| column_name | dtype | lgpd_classification | risk_level | recommended_action | reason |
| --- | --- | --- | --- | --- | --- |
| order_id | object | personal_data | high | mask | No personal-data indicators found in column name. Regex matched phone pattern in sampled values. |
| order_item_id | int64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| customer_unique_id | object | personal_data | high | mask | No personal-data indicators found in column name. Regex matched phone pattern in sampled values. |
| order_status | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| order_purchase_timestamp | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| order_delivered_customer_date | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| order_estimated_delivery_date | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| order_date | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| order_year | int64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| order_month | int64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| purchase_cohort_month | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| cohort_order_month_number | int64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| customer_order_sequence | int64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| is_first_order | bool | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| seller_key | object | personal_data | high | mask | No personal-data indicators found in column name. Regex matched phone pattern in sampled values. |
| seller_volume_tier | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| seller_order_count | int64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| seller_avg_delivery_days | float64 | personal_data | high | mask | No personal-data indicators found in column name. Regex matched CNPJ pattern in sampled values. |
| seller_delay_rate | float64 | personal_data | high | mask | No personal-data indicators found in column name. Regex matched phone pattern in sampled values. |
| delivery_time_days | float64 | personal_data | high | mask | No personal-data indicators found in column name. Regex matched CNPJ pattern in sampled values. |
| seller_dispatch_time_days | float64 | personal_data | high | mask | No personal-data indicators found in column name. Regex matched CNPJ pattern in sampled values. |
| carrier_delivery_time_days | float64 | personal_data | high | mask | No personal-data indicators found in column name. Regex matched CNPJ pattern in sampled values. |
| estimated_delay_days | float64 | personal_data | high | mask | No personal-data indicators found in column name. Regex matched CNPJ pattern in sampled values. |
| is_delayed | bool | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| price | float64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| freight_value | float64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| freight_to_price_ratio | float64 | personal_data | high | mask | No personal-data indicators found in column name. Regex matched CNPJ pattern in sampled values. |
| total_item_value | float64 | personal_data | high | mask | No personal-data indicators found in column name. Regex matched CNPJ pattern in sampled values. |
| payment_type_mode | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| review_score_mean | float64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| product_category_name | object | personal_data | high | mask | Column name indicates personal data. No personal-data regex pattern matched sampled values. |
| product_category_name_english | object | personal_data | high | mask | Column name indicates personal data. No personal-data regex pattern matched sampled values. |
| customer_state | object | indirect_identifier | medium | review | Column name indicates indirect identification risk. No personal-data regex pattern matched sampled values. |
| seller_state | object | indirect_identifier | medium | review | Column name indicates indirect identification risk. No personal-data regex pattern matched sampled values. |

## Governance Recommendations

- Apply masking for direct identifiers in shared datasets.
- Anonymize or remove sensitive columns from executive layers.
- Review null patterns in critical personal-data columns.
- Document legal basis and retention policy for personal data usage.
- Block publication until masking/anonymization controls are implemented.