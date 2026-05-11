# ADR-004: Streamlit for Executive Governance Interface

## Status
Accepted

## Context
The project needs a fast, local-first executive interface to surface governance KPIs, privacy risk, data quality controls, and publication decisions to non-technical stakeholders.

The scope is portfolio/demo, so implementation speed, maintainability, and Python-native integration are priorities. A full custom web frontend would require a separate frontend stack, increasing complexity without proportional benefit for this use case.

## Decision
Use Streamlit as the sole UI framework for executive governance delivery, organized as a multi-page app with a shared data context loaded once per session.

## Consequences

- Fast iteration in pure Python with direct integration to pandas and Plotly.
- Low frontend complexity and straightforward local setup.
- Less UI customization compared to a full custom web frontend.
- Streamlit's session model simplifies shared context (data loading, classification, quality checks run once via `@st.cache_data`).
- Deployment to Streamlit Community Cloud requires no infrastructure management.

## Alternatives Considered

- **Flask/FastAPI + SPA frontend** — more flexible but much higher complexity and maintenance overhead for a portfolio project.
- **Dash-based application** — viable Python alternative but more boilerplate and less community momentum for governance use cases.
