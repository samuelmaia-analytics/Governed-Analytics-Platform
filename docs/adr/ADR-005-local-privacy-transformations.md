# ADR-005: Local Privacy Transformations Without External APIs

## Status
Accepted

## Context
The project must run entirely locally, use only synthetic or public demo data, and avoid paid or external service dependencies. Privacy controls need deterministic, reproducible behavior for automated tests and portfolio demonstration.

External privacy/anonymization APIs would introduce network calls, API keys, cost, and non-determinism — all incompatible with local-first CI and offline reproducibility.

## Decision
Implement all privacy transformations locally in `src/privacy_transformations.py` using deterministic hashing (pseudonymization), masking patterns, and removal logic. No external APIs are called during transformation.

## Consequences

- No external data exposure and no service cost.
- Reproducible CI and local execution with a simple `make install && make test` setup.
- Transformation behavior is fully testable with unit tests.
- Fewer advanced capabilities than managed privacy platforms (e.g., no format-preserving encryption, no differential privacy).
- Acceptable trade-off for portfolio scope.

## Alternatives Considered

- **External privacy/anonymization APIs** (e.g., managed PII detection services) — incompatible with local-first, cost-free requirements.
- **Manual spreadsheet-based transformations** — not reproducible, not testable, not auditable.
