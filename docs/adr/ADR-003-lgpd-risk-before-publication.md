# ADR-003: LGPD-Inspired Risk Gate Before Publication

## Status
Accepted

## Context
Executive publication without an explicit privacy-risk gate can expose sensitive or insufficiently protected fields.

## Decision
Require a publication gate decision based on:

- data quality score;
- privacy risk score;
- critical rule failures;
- freshness status;
- schema contract status;
- sensitive data protection checks.

Generate a publication decision artifact under `data/published/monitoring/publication_decision.json`.

## Consequences

- Publication status becomes explicit (`Approved`, `Needs Review`, `Blocked`).
- Governance decisions gain traceability in monitoring artifacts.
- This remains a simulated, portfolio-grade control and does not replace legal approval workflows.
