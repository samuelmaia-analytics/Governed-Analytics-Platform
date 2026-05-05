# ADR-002: YAML Data Quality Contracts

## Status
Accepted

## Context
Governance checks need readable, versioned, and reviewable rules with low operational friction.

## Decision
Use YAML contracts for dataset-level quality and publication criteria, validated by automated tests and pipeline checks.

## Consequences

- Rules are auditable and easy to review in pull requests.
- Contract evolution is explicit and traceable.
- Requires discipline to keep YAML contracts aligned with implemented datasets.
