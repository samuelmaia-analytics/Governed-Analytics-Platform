# 001 - Why Streamlit for Executive Governance

## Context
- The project needs a fast, local-first executive interface for governance KPIs, privacy risk, quality controls, and publication decisions.
- The scope is portfolio/demo, so implementation speed and maintainability are priorities.

## Decision
- Use Streamlit as the main UI framework for executive governance delivery.

## Consequences
- Fast iteration in pure Python with direct integration to pandas/Plotly.
- Low frontend complexity and easier local setup.
- Less UI customization than a full custom web frontend.

## Alternatives considered
- Flask/FastAPI + SPA frontend.
- Dash-based application.
