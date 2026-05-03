# ADR-001: Streamlit for Executive Governance Delivery

## Context
- The project needs an interactive executive interface to present governance KPIs, privacy risk, data quality controls, and publication decisions.
- The solution must be local-first, fast to iterate, and simple for portfolio/demo usage.

## Decision
- Use Streamlit as the primary UI layer for governance delivery (`app/main.py` and pages under `app/pages`).

## Consequences
- Faster delivery of a usable governance product with minimal frontend overhead.
- Native integration with pandas/Plotly and Python modules already used in the pipeline.
- Limited fine-grained frontend control compared to full SPA stacks, but acceptable for the project scope.

## Alternatives considered
- Flask/FastAPI + custom frontend: more control, higher implementation and maintenance cost.
- Dash: good for analytics apps, but less aligned with existing repo patterns and simpler Streamlit navigation model.
