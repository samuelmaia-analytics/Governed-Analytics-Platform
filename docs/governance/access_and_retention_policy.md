# Access and Retention Policy (Portfolio Scope)

This document defines a portfolio-grade access and retention model for the Governed Analytics Platform.
It is intended to demonstrate governance engineering practices, not legal or compliance advice.

## Scope

- Covers local artifacts under `data/` and governance outputs under `docs/`.
- Applies to the simulated analytical publication flow in this repository.
- Complements `docs/privacy_governance.md`.

## Access model (persona-based)

| Persona | Curated/Internal Layer | Published Layer | Contracts & Docs | Notes |
| --- | --- | --- | --- | --- |
| Data Engineer / Analytics Engineer | Read/Write | Read/Write | Read/Write | Owns pipeline, contracts, publication controls |
| Data Analyst / BI Analyst | Read (approved assets only) | Read | Read | Should consume `published/*` for executive analysis |
| Business Stakeholder / Executive | No direct access | Read (dashboard outputs) | Read (summaries) | Consumes KPIs and governance summaries |
| Auditor / Governance Reviewer | Read | Read | Read | Reviews traceability and control evidence |

## Retention guidance

| Artifact Type | Location | Recommended Retention | Rationale |
| --- | --- | --- | --- |
| Raw landing source files | `data/raw/landing/` | Keep reproducible snapshot for project lifecycle | Reproducibility and lineage validation |
| Standardized and curated artifacts | `data/standardized/`, `data/curated/` | Keep latest + selected historical snapshots | Technical debugging and reconciliation |
| Published analytical layer | `data/published/` | Keep current + periodic historical snapshots | Executive reporting traceability |
| Monitoring and governance logs | `data/published/monitoring/`, `docs/` | Keep historical records | Auditability of quality/privacy decisions |

## Operational controls

- Prefer consumption from `data/published/` in executive-facing use cases.
- Restrict direct exposure of `data/curated/analytics/` in presentation layers.
- Enforce publication checks before promoting published assets.
- Keep policy/version changes in Git history for traceability.

## Limitations

- This repository demonstrates **LGPD-inspired controls** in a public dataset context.
- It does not include enterprise IAM, legal retention obligations, or jurisdiction-specific legal enforcement.
