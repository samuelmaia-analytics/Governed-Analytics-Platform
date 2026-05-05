# Governed Analytics Platform

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/ci.yml)
[![Lint](https://img.shields.io/badge/Lint-Ruff-2D2D2D?logo=ruff&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/lint.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Coverage](https://codecov.io/gh/samuelmaia-analytics/Governed-Analytics-Platform/branch/main/graph/badge.svg)](https://codecov.io/gh/samuelmaia-analytics/Governed-Analytics-Platform)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live-red?logo=streamlit)](https://governed-analytics-platform.streamlit.app/)

**Language:** `English` | [Português](README.pt-BR.md)

Portfolio-grade governed analytics platform focused on Analytics Engineering, Data Governance, LGPD-inspired controls, data quality, and executive delivery.

## Executive Summary

This project transforms relational CSV inputs into a privacy-aware published analytical layer.
It combines:

- modular data pipeline;
- LGPD-inspired classification;
- explainable privacy risk scoring;
- data quality controls;
- publication decision states;
- Streamlit executive app;
- testing and CI quality gates.

## Business Impact

- Reduces exposure risk by separating internal analytics from published executive consumption.
- Improves trust with explicit publication status (`Approved`, `Needs Review`, `Blocked`).
- Accelerates technical review with reproducible governance evidence.
- Demonstrates product-oriented analytics engineering, not only dashboarding.

## Why this project matters

Many portfolio projects stop at visual output.
This repository demonstrates the governed journey from ingestion to controlled publication.

## Architecture Overview

Core flow:

ingestion -> standardization -> analytical enrichment -> data quality checks -> LGPD-inspired classification -> explainable risk score -> controlled publication -> executive app.

Key boundary:

the app consumes the published layer (`data/published/dashboard`) instead of the full internal curated layer.

```mermaid
flowchart LR
    A[Raw Data] --> B[src/data_loader.py]
    B --> C[src/lgpd_classifier.py]
    B --> D[src/data_quality.py]
    C --> E[src/risk_scoring.py]
    D --> F[src/report_generator.py]
    E --> F
    B --> G[app/main.py]
    C --> G
    D --> G
    E --> G
```

## Implemented vs Simulated

### Implemented

- Modular Python pipeline with reproducible execution.
- Column classification by heuristics plus YAML contract rules.
- Explainable privacy risk score and publication decision logic.
- Rule-based quality checks and governance evidence artifacts.
- Streamlit executive views including publication rationale.
- Tests, linting, mypy checks, and CI workflows.

### Simulated

- Processing inventory metadata (controller/operator/DPO) with fictional entities.
- Mini RIPD document for demonstration.
- Legal basis and retention model represented for governance simulation.
- Full enterprise IAM and centralized audit platform integration.

## Production Readiness Boundaries

- This is a **production-inspired portfolio project**.
- It uses **sample, synthetic, or public data only**.
- It **does not process real personal data**.
- It demonstrates engineering patterns such as:
  - data contracts;
  - quality gates;
  - LGPD-inspired classification;
  - observability;
  - lineage;
  - CI/CD.
- It is **not** a live enterprise production system.

## What this project demonstrates

- Analytics Engineering mindset with governance-by-design.
- Clear internal vs published data boundaries.
- Reproducible local run with quality gates.
- Executive communication of risk, quality, and publication readiness.

## How to run locally

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
make test
make app
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
make install
copy .env.example .env
make test
make app
```

## How to review this project in 5 minutes

1. Read until **Implemented vs Simulated**.
2. Open `docs/architecture.md` and `docs/privacy_governance.md`.
3. Run `make test`.
4. Open the Streamlit app and inspect **Governance Control Center**.
5. Review `docs/semantic_layer.md` and `docs/recruiter_summary.md`.

## Streamlit Executive App

Main pages:

- Executive Overview
- Data Catalog
- LGPD & Privacy Risk
- Data Quality
- EDA
- Governance Report
- Governance Control Center

## Main Structure

| Path | Purpose |
| --- | --- |
| `app/` | Streamlit executive interface |
| `src/` | Pipeline and governance logic |
| `contracts/` | Data quality and governance contracts |
| `docs/` | Technical and executive documentation |
| `tests/` | Automated tests |
| `.github/workflows/` | CI/CD |
| `powerbi/` | BI export artifacts |

## Recruiter Notes

Strong interview discussion artifact for:

- Analytics Engineer
- Data Engineer
- Data Governance / Data Platform profiles
- Senior Data Analyst roles with ownership scope

## Links

- Streamlit app: <https://governed-analytics-platform.streamlit.app/>
- Repository: <https://github.com/samuelmaia-analytics/Governed-Analytics-Platform>
- Technical docs index: [docs/README.en.md](docs/README.en.md)
