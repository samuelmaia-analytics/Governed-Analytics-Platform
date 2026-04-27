# LGPD Controls

- Generated at: **2026-04-27 12:46:34 UTC**
- Risk score: **87 / 100**
- Risk level: **high**

## Dataset Summary

- Total rows: **10**
- Total columns: **16**
- Risk summary: Dataset with 7 personal, 1 sensitive and 2 indirect identifier columns over 10 rows.

## LGPD Classification by Column

| column_name | dtype | lgpd_classification | risk_level | recommended_action | reason |
| --- | --- | --- | --- | --- | --- |
| customer_id | object | personal_data | high | mask | Column name indicates personal data. No personal-data regex pattern matched sampled values. |
| customer_name | object | personal_data | high | mask | Column name indicates personal data. No personal-data regex pattern matched sampled values. |
| customer_email | object | personal_data | high | mask | Column name indicates personal data. Regex matched email pattern in sampled values. |
| customer_phone | object | personal_data | high | mask | Column name indicates personal data. Regex matched phone pattern in sampled values. |
| state | object | indirect_identifier | medium | review | Column name indicates indirect identification risk. No personal-data regex pattern matched sampled values. |
| city | object | indirect_identifier | medium | review | Column name indicates indirect identification risk. No personal-data regex pattern matched sampled values. |
| birth_date | object | personal_data | high | mask | Column name indicates personal data. No personal-data regex pattern matched sampled values. |
| order_id | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| order_date | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| revenue | float64 | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| payment_method | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| status | object | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| marketing_consent | bool | non_personal | low | keep | No personal-data indicators found in column name. No personal-data regex pattern matched sampled values. |
| last_login_ip | object | personal_data | high | mask | Column name indicates personal data. Regex matched IP pattern in sampled values. |
| cpf | object | personal_data | high | remove | Column name indicates personal data. Regex matched CPF pattern in sampled values. |
| saude_score | int64 | sensitive_personal_data | high | anonymize | Column name indicates sensitive data. No personal-data regex pattern matched sampled values. |

## Governance Recommendations

- Apply masking for direct identifiers in shared datasets.
- Anonymize or remove sensitive columns from executive layers.
- Review null patterns in critical personal-data columns.
- Document legal basis and retention policy for personal data usage.