# Case Study: Governed Analytics Platform

## Business Context

Analytics teams usually optimize for delivery speed.
When governance is deferred, dashboards can expose excessive detail and inconsistent metrics.

This case models a governance-first approach for executive analytics publication.

## Problem

- No clear boundary between internal analytics and executive exposure.
- Limited privacy rationale for published columns.
- Weak publication criteria beyond visualization readiness.

## Solution

The platform applies a controlled publication pipeline:

1. classify columns (heuristic + YAML contract);
2. compute explainable privacy risk score;
3. run data quality checks;
4. produce publication decision (`Approved`, `Needs Review`, `Blocked`);
5. expose only published, minimized data in Streamlit.

## Architecture Decision

Internal `curated` layer remains richer for engineering analysis.
Executive app consumes only `published/dashboard`.

This allows stricter control over what is exposed and simplifies governance review.

## Governance Evidence

- privacy controls documentation: `docs/privacy_governance.md`
- semantic layer dictionary: `docs/semantic_layer.md`
- quality report: `docs/data_quality_report.md`
- contracts: `contracts/governance/` and `contracts/data_quality_rules.yml`

## What Is Implemented

- reproducible Python pipeline
- privacy-aware publication controls
- quality checks and evidence artifacts
- executive app with publication decision rationale
- tests + lint + CI gates

## What Is Simulated

- legal metadata (controller/operator/dpo) with fictional entities
- mini RIPD document for portfolio use
- enterprise governance workflow integration

## Outcome

The project demonstrates a production-oriented analytics product posture:
clear data boundaries, explicit decisioning, and transparent controls.
