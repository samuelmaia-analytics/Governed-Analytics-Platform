# Data Quality Report

- Generated at: **2026-04-27 12:46:34 UTC**
- Total rows: **10**
- Total columns: **16**
- Failed checks: **0**

## Quality Checks

| check_name | status | severity | affected_columns | affected_rows | recommendation |
| --- | --- | --- | --- | --- | --- |
| high_null_columns_over_30pct | PASS | low |  | 0 | Review source completeness and enforce mandatory fields for critical columns. |
| duplicate_rows | PASS | low |  | 0 | Remove duplicates and validate ingestion keys/grain assumptions. |
| constant_columns | PASS | low |  | 0 | Drop or review constant columns to simplify the analytical model. |
| negative_values__revenue | PASS | low | revenue | 0 | Validate business rule and fix negative values or document accepted exceptions. |
| negative_values__saude_score | PASS | low | saude_score | 0 | Validate business rule and fix negative values or document accepted exceptions. |
| future_dates__birth_date | PASS | low | birth_date | 0 | Correct reference dates or ensure timezone/calendar conventions are applied. |
| future_dates__order_date | PASS | low | order_date | 0 | Correct reference dates or ensure timezone/calendar conventions are applied. |

## Risks Found

- Failed checks count: **0**
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