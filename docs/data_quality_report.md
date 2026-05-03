# Data Quality Report

- Generated at: **2026-05-03 20:54:28 UTC**
- Total rows: **10**
- Total columns: **16**
- Failed checks: **1**

## Quality Checks

| check_name | status | severity | affected_columns | affected_rows | recommendation | rule_source |
| --- | --- | --- | --- | --- | --- | --- |
| high_null_columns_over_30pct | PASS | low |  | 0 | Review source completeness and enforce mandatory fields for critical columns. | built_in |
| duplicate_rows | PASS | low |  | 0 | Remove duplicates and validate ingestion keys/grain assumptions. | built_in |
| constant_columns | PASS | low |  | 0 | Drop or review constant columns to simplify the analytical model. | built_in |
| negative_values__revenue | PASS | low | revenue | 0 | Validate business rule and fix negative values or document accepted exceptions. | built_in |
| negative_values__saude_score | PASS | low | saude_score | 0 | Validate business rule and fix negative values or document accepted exceptions. | built_in |
| future_dates__birth_date | PASS | low | birth_date | 0 | Correct reference dates or ensure timezone/calendar conventions are applied. | built_in |
| future_dates__order_date | PASS | low | order_date | 0 | Correct reference dates or ensure timezone/calendar conventions are applied. | built_in |
| order_id_not_null | PASS | low | order_id | 0 | Fill or remediate missing order identifiers before publication. | contracts\data_quality_rules.yml |
| order_id_unique | PASS | low | order_id | 0 | Ensure order identifiers are unique in the analytical grain. | contracts\data_quality_rules.yml |
| revenue_accepted_range | PASS | low | revenue | 0 | Review outlier revenue records and business rule boundaries. | contracts\data_quality_rules.yml |
| order_date_no_future | PASS | low | order_date | 0 | Correct records with future dates before publication. | contracts\data_quality_rules.yml |
| revenue_no_negative | PASS | low | revenue | 0 | Negative revenue should be justified or corrected. | contracts\data_quality_rules.yml |
| customer_email_max_null | PASS | low |  | 0 | Improve email completeness or document expected null rates. | contracts\data_quality_rules.yml |
| order_status_allowed_values | FAIL | medium | order_status | 0 | Standardize order status values according to contract. | contracts\data_quality_rules.yml |

## Risks Found

- Failed checks count: **1**
- Columns with >30% nulls: **none**
- Duplicate rows: **0**

## Next Steps

- Prioritize high-severity failed checks and assign owners.
- Create remediation SLA for duplicated records and null critical fields.
- Automate recurring quality checks in CI/CD and monitoring jobs.

## Dataset Overview

| total_rows | total_columns | numeric_columns | categorical_columns | datetime_columns |
| --- | --- | --- | --- | --- |
| 10 | 16 | 2 | 13 | 0 |