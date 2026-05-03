# ADR-004: Local/Demo Privacy Transformations Without External APIs

## Context
- The project must run locally with synthetic data and avoid paid services or external dependencies.
- Privacy transformations should be deterministic, testable, and safe for portfolio demonstration.

## Decision
- Implement masking/anonymization locally in `src/privacy_transformations.py` and avoid external APIs for transformation logic.

## Consequences
- Reproducible runs, no external data exposure, and no service cost.
- Straightforward unit testing and CI behavior.
- Fewer advanced transformation capabilities than specialized managed services, acceptable for demo scope.

## Alternatives considered
- External privacy API services: richer features, conflicts with cost/privacy/local-run constraints.
- Manual spreadsheet transformations: low engineering rigor and weak repeatability.
