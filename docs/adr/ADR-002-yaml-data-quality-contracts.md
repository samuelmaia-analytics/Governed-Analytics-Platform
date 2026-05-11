# ADR-002: YAML Data Quality Contracts

## Status
Accepted

## Context
Data quality rules must be explicit, auditable, and easy to evolve without code rewrites. Governance reviews benefit from declarative rules in version control that non-technical stakeholders can inspect.

Hardcoding quality rules in Python makes them opaque and harder to evolve collaboratively. Storing them in an external database introduces infrastructure dependencies incompatible with the local-first, reproducible setup of this project.

## Decision
Define all dataset-level quality rules in YAML contracts under `contracts/` and execute them via `src/data_quality_rules.py`. Each contract covers column types, null thresholds, primary key constraints, minimum row counts, and business-level checks.

## Consequences

- Rules are auditable and easy to review in pull requests.
- Contract evolution is explicit and traceable in version history.
- Non-code stakeholders can review rule intent directly in YAML.
- Requires discipline to keep YAML contracts aligned with implemented datasets.
- Malformed contracts are caught by automated validation tests.

## Alternatives Considered

- **Python-only hardcoded rules** — opaque, harder to audit, require code changes for every rule update.
- **Rule storage in an external database/service** — introduces infrastructure dependency and breaks local-first reproducibility.
