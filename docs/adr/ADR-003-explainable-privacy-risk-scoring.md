# ADR-003: Explainable Privacy Risk Scoring

## Context
- Publication decisions involve LGPD-sensitive data and must be defensible.
- A single opaque score is not enough for governance review, remediation planning, or recruiter evaluation of engineering maturity.

## Decision
- Keep privacy scoring explainable by returning score components, per-component points, risk level, rationale, recommendations, and publication recommendation (`src/risk_scoring.py`).

## Consequences
- Better auditability and clearer decision rationale in Streamlit and reports.
- Easier triage of mitigation actions (mask, anonymize, remove, review).
- Slightly larger response payload and more tests to maintain.

## Alternatives considered
- Black-box aggregate score only: simpler output, poor governance transparency.
- Manual qualitative assessment only: explainable, but inconsistent and hard to automate.
