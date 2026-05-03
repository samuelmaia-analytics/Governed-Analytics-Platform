# ADR-002: YAML Contracts for Data Quality Rules

## Context
- Data quality checks must be explicit, reviewable, and easy to change without rewriting core Python logic.
- The project needs a declarative format suitable for governance communication and version control.

## Decision
- Define rule contracts in YAML (`contracts/data_quality_rules.yml`) and execute them through `src/data_quality_rules.py`.

## Consequences
- Rules become auditable and readable by technical and non-technical stakeholders.
- New checks can be added by editing contracts instead of duplicating code paths.
- Requires schema discipline and tests to prevent invalid rule definitions.

## Alternatives considered
- Hardcoded checks only in Python: simpler initially, weaker governance traceability.
- Rules in database: more dynamic, unnecessary operational complexity for local/demo scope.
