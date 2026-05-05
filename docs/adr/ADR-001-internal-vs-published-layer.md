# ADR-001: Internal vs Published Layer Boundary

## Status
Accepted

## Context
The project transforms relational operational data into analytics outputs. Exposing internal curated datasets directly would increase privacy and governance risk.

## Decision
Maintain a strict separation:

- internal analytical layer (`curated`) for transformation and governance processing;
- published layer (`published/dashboard` and `published/semantic`) for executive and BI consumption.

## Consequences

- Better exposure control and governance review before publication.
- Clear boundary for contracts and publication policies.
- Slightly higher pipeline complexity due to an extra publication stage.
