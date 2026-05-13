# Data Quality Report

- Generated at: **2026-05-11 17:35:32 UTC**
- Total rows: **112650**
- Total columns: **34**
- Failed checks: **5**

## Quality Checks

| check_name | status | severity | affected_columns | affected_rows | recommendation | rule_source |
| --- | --- | --- | --- | --- | --- | --- |
| high_null_columns_over_30pct | PASS | low |  | 0 | Review source completeness and enforce mandatory fields for critical columns. | built_in |
| duplicate_rows | PASS | low |  | 0 | Remove duplicates and validate ingestion keys/grain assumptions. | built_in |
| constant_columns | PASS | low |  | 0 | Drop or review constant columns to simplify the analytical model. | built_in |
| negative_values__price | PASS | low | price | 0 | Validate business rule and fix negative values or document accepted exceptions. | built_in |
| negative_values__freight_value | PASS | low | freight_value | 0 | Validate business rule and fix negative values or document accepted exceptions. | built_in |
| negative_values__freight_to_price_ratio | PASS | low | freight_to_price_ratio | 0 | Validate business rule and fix negative values or document accepted exceptions. | built_in |
| negative_values__total_item_value | PASS | low | total_item_value | 0 | Validate business rule and fix negative values or document accepted exceptions. | built_in |
| negative_values__review_score_mean | PASS | low | review_score_mean | 0 | Validate business rule and fix negative values or document accepted exceptions. | built_in |
| future_dates__order_purchase_timestamp | PASS | low | order_purchase_timestamp | 0 | Correct reference dates or ensure timezone/calendar conventions are applied. | built_in |
| future_dates__order_delivered_customer_date | PASS | low | order_delivered_customer_date | 0 | Correct reference dates or ensure timezone/calendar conventions are applied. | built_in |
| future_dates__order_estimated_delivery_date | PASS | low | order_estimated_delivery_date | 0 | Correct reference dates or ensure timezone/calendar conventions are applied. | built_in |
| future_dates__order_date | PASS | low | order_date | 0 | Correct reference dates or ensure timezone/calendar conventions are applied. | built_in |
| order_id_not_null | PASS | low | order_id | 0 | Fill or remediate missing order identifiers before publication. | contracts\data_quality_rules.yml |
| order_id_unique | FAIL | high | order_id | 23787 | Ensure order identifiers are unique in the analytical grain. | contracts\data_quality_rules.yml |
| revenue_accepted_range | FAIL | medium | revenue | 0 | Review outlier revenue records and business rule boundaries. | contracts\data_quality_rules.yml |
| order_date_no_future | PASS | low | order_date | 0 | Correct records with future dates before publication. | contracts\data_quality_rules.yml |
| revenue_no_negative | FAIL | medium | revenue | 0 | Negative revenue should be justified or corrected. | contracts\data_quality_rules.yml |
| customer_email_max_null | FAIL | low | customer_email | 0 | Improve email completeness or document expected null rates. | contracts\data_quality_rules.yml |
| order_status_allowed_values | FAIL | medium | order_status | 369 | Standardize order status values according to contract. | contracts\data_quality_rules.yml |
| order_status_not_null | PASS | low | order_status | 0 | Order status is required before publication. | contracts\data_quality_rules.yml |
| order_date_max_null | PASS | low |  | 0 | Order date completeness must stay above 95% for publication. | contracts\data_quality_rules.yml |

## Risks Found

- Failed checks count: **5**
- Columns with >30% nulls: **none**
- Duplicate rows: **0**

## Next Steps

- Prioritize high-severity failed checks and assign owners.
- Create remediation SLA for duplicated records and null critical fields.
- Automate recurring quality checks in CI/CD and monitoring jobs.

## Dataset Overview

| total_rows | total_columns | numeric_columns | categorical_columns | datetime_columns |
| --- | --- | --- | --- | --- |
| 112650 | 34 | 17 | 15 | 0 |