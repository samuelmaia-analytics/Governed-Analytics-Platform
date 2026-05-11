# ADR-003: LGPD-Inspired Risk Gate Before Publication

## Status
Accepted

## Context
Executive publication without an explicit privacy-risk gate can expose sensitive or insufficiently protected fields. Privacy publication decisions must also be defensible for governance and compliance discussions — a single opaque score is insufficient for remediation planning.

## Decision
Require a publication gate decision before any data reaches the published layer, based on six signals:

- data quality score;
- privacy risk score (explainable, with per-component breakdown);
- critical rule failures;
- freshness status;
- schema contract status;
- sensitive data protection checks.

Generate a publication decision artifact under `data/published/monitoring/publication_decision.json` and expose the rationale in the Streamlit Governance Control Center.

## Consequences

- Publication status becomes explicit (`Approved`, `Needs Review`, `Blocked`).
- Governance decisions gain traceability in monitoring artifacts.
- Risk score components enable targeted remediation (mask, remove, pseudonymize).
- Clearer executive storytelling and auditability.
- Slightly more output complexity and testing effort compared to a single-metric gate.
- This remains a simulated, portfolio-grade control and does not replace legal approval workflows.

## Alternatives Considered

- **Black-box aggregate score only** — insufficient for explaining which controls failed and what remediation is needed.
- **Fully manual qualitative assessment** — not reproducible, not testable, and does not scale.
