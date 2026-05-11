# 002 - Why YAML Contracts for Data Quality

## Context
- Data quality rules must be explicit, auditable, and easy to evolve without code rewrites.
- Governance reviews benefit from declarative rules in version control.

## Decision
- Define rules in YAML contracts and execute them via `src/data_quality_rules.py`.

## Consequences
- Better traceability and easier rule maintenance.
- Non-code stakeholders can review rule intent.
- Requires validation/tests to catch malformed contracts.

## Alternatives considered
- Python-only hardcoded rules.
- Rule storage in external database/service.

