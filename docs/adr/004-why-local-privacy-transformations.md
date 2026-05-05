# 004 - Why Local Privacy Transformations

## Context
- The project must run locally, use synthetic/demo data, and avoid paid/external dependencies.
- Privacy controls need deterministic behavior for tests and portfolio reproducibility.

## Decision
- Implement privacy transformations locally in `src/privacy_transformations.py` and avoid external APIs.

## Consequences
- No external data exposure and no service cost.
- Reproducible CI/local execution with simple setup.
- Fewer advanced capabilities than managed privacy platforms.

## Alternatives considered
- External privacy/anonymization APIs.
- Manual spreadsheet-based transformations.

