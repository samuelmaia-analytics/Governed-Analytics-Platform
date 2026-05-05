# Governed Analytics Platform

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/ci.yml)
[![Lint](https://img.shields.io/badge/Lint-Ruff-2D2D2D?logo=ruff&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/lint.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Coverage](https://codecov.io/gh/samuelmaia-analytics/Governed-Analytics-Platform/branch/main/graph/badge.svg)](https://codecov.io/gh/samuelmaia-analytics/Governed-Analytics-Platform)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live-red?logo=streamlit)](https://governed-analytics-platform.streamlit.app/)
[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform)

**Language:** [PT-BR](README.md) | `EN`

A governed Streamlit analytics platform that demonstrates Data Governance, LGPD classification, data quality, automated EDA, and executive reporting.

> This is not only a dashboard. It is an Analytics Engineering case with governance, quality controls, privacy classification, explainable risk scoring, a published layer, and executive delivery.

## Executive Positioning

This repository simulates an executive-ready governed analytics product: privacy-aware, quality-gated, auditable, and explainable for publication decisions.

## TL;DR

- focus: Analytics Engineering with governance controls from ingestion to published layer;
- delivery: Streamlit app, Python pipeline, contracts, and operational docs;
- audience: data engineering, analytics, and technical leadership.

## How to review in 5 minutes

1. Read **Business Problem** and **Solution**.
2. Check the pipeline and layer separation in **Architecture Summary** and `docs/architecture.md`.
3. Run locally with `make install`, `make test`, and `make app`.
4. Open the app and inspect **Executive Overview**, **LGPD & Privacy Risk**, **Data Quality**, and **Governance Control Center**.
5. Validate governance evidence in `docs/privacy_governance.md`, `docs/data_quality_report.md`, and `docs/semantic_layer.md`.

## Recruiter Quick View

- Governed analytics product, not only a dashboard.
- Modular Python pipeline from ingestion to published layer.
- Column-level LGPD classification.
- Explainable privacy risk scoring.
- Declarative YAML-based data quality rules.
- Data Quality Score and publication decision in the app.
- Privacy masking/anonymization preview in the interface.
- Automated screenshots with Playwright.
- Tests, CI, Ruff, Pytest, and reproducible local execution.

## Business Problem

Analytics teams often accelerate delivery without formal controls for quality, privacy, and traceability. This creates regulatory risk, low trust in data assets, and weak governance for executive decisions.

## Solution

The project implements a governed analytics product approach:

- explicit boundary between internal and published layers;
- column-level LGPD classification with privacy risk scoring;
- reusable data quality checks;
- automated EDA for analytical acceleration;
- Markdown reports for technical and executive governance.

## Problem -> Solution -> Evidence

| Problem | Solution | Evidence |
| --- | --- | --- |
| Analytics delivery without a clear exposure boundary | Internal (`curated`) and published (`published`) layers are explicitly separated | `docs/architecture.md`, `src/publish_dashboard.py` |
| Unnecessary data exposure risk | Data minimization + pseudonymization before publication | `docs/privacy_governance.md`, `contracts/governance/privacy_governance.json` |
| Inconsistent data quality between processing and consumption | Declarative quality rules + automated checks in pipeline | `contracts/data_quality_rules.yml`, `src/data_quality_rules.py`, `tests/test_data_quality_rules.py` |
| Ambiguous decision metrics | Published semantic layer with documented KPI definitions | `src/semantic_layer.py`, `docs/semantic_layer.md` |
| Low operational confidence | CI, lint, tests, and release/rollback runbooks | `.github/workflows/`, `docs/release_runbook.md`, `docs/rollback_runbook.md` |

## Architecture Summary

1. `src/data_loader.py` reads synthetic sample datasets.
2. `src/lgpd_classifier.py` classifies columns by LGPD category.
3. `src/risk_scoring.py` computes explainable privacy risk score and publication recommendation.
4. `src/data_quality.py` + `src/data_quality_rules.py` run built-in and YAML-driven quality checks.
5. `src/report_generator.py` materializes governance artifacts in `docs/`.
6. `app/main.py` exposes executive governance pages in Streamlit.

## Core Features

- Executive Overview with governance KPIs.
- Data Catalog with metadata and column dictionary.
- LGPD & Privacy Risk with recommendations.
- Data Quality checks with severity and status.
- EDA (descriptive stats, null profile, outliers, correlation).
- Governance Report generated in `docs/`.
- Domain-versioned LGPD policies under `contracts/governance/policies/`.
- Contract-driven business rules under `contracts/governance/business_rules/`.
- Automated technical lineage in `data/curated/catalog/technical_lineage.json`.
- Dataset governance scorecards in `data/published/monitoring/governance_scorecards.csv`.
- Governance Control Center page with publication readiness and top risk actions.
- Privacy transformation module (`src/privacy_transformations.py`) with masking/anonymization actions.
- Governance run history (`data/published/monitoring/governance_history.csv`) for traceability.

## What This Demonstrates to Recruiters

- Analytics engineering with reproducible governance controls.
- LGPD-oriented privacy-by-design in analytical products.
- Contract/rule-driven data quality validation.
- Typed Python modules, tests, CI compatibility, and executive UX delivery.

## Operational Governance (implemented)

- domain-level LGPD policy versioning enforced in publication flow;
- contract-based business rule validation with dedicated report;
- automated technical lineage integrated into the technical catalog;
- scheduled governance scorecards per dataset.

## Main Structure

| Path | Purpose |
| --- | --- |
| `app/` | modern executive Streamlit app |
| `src/` | analytics engineering and governance modules |
| `data/samples/` | synthetic demonstration dataset |
| `docs/` | governance reports and technical docs |
| `tests/` | automated test suite |

## Run Locally

```bash
make install
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
copy .env.example .env
```

## Run Apps

Executive app:

```bash
make app
```

## Minimal local run

```bash
make install
make test
make app
```

## Testing and Quality Gates

```bash
make lint
python -m mypy src/data_loader.py src/data_quality.py src/eda.py src/lgpd_classifier.py src/risk_scoring.py src/report_generator.py src/governance_types.py app/main.py app/context.py app/components/cards.py app/pages/data_catalog.py app/pages/data_quality.py app/pages/eda.py app/pages/executive_overview.py app/pages/governance_report.py app/pages/lgpd_privacy_risk.py
make test
```

Highlighted tests:

- `tests/test_lgpd_classifier.py`
- `tests/test_risk_scoring.py`
- `tests/test_data_quality.py`
- `tests/test_privacy_transformations.py`
- `tests/test_data_quality_rules.py`
- `tests/test_governance_history.py`

## Governance Features

- Explainable privacy score components and recommendations.
- Declarative quality checks (`contracts/data_quality_rules.yml`).
- Publication decision states: `Approved`, `Needs Review`, `Blocked`.
- Monitoring history append function: call `src.governance_history.append_governance_history`.

```bash
python -c "from pathlib import Path; import pandas as pd; from src.data_quality import run_data_quality_checks; from src.lgpd_classifier import classify_dataframe_columns; from src.governance_history import append_governance_history_from_dataframes; df = pd.read_csv('data/samples/sample_governance_dataset.csv'); classification = classify_dataframe_columns(df); quality = run_data_quality_checks(df); append_governance_history_from_dataframes(df=df, classification_df=classification, quality_result=quality, publication_status='Needs Review'); print(Path('data/published/monitoring/governance_history.csv').resolve())"
```

## Case Study Snapshot

Given a synthetic commerce dataset with personal identifiers and quality issues, the platform classifies privacy exposure, executes quality checks, summarizes governance risk, and provides a clear publication decision with recommended remediation actions.

## Screenshots

### Executive Overview
![Executive Overview](assets/screenshots/executive_overview.png)

### LGPD & Privacy Risk
![LGPD & Privacy Risk](assets/screenshots/lgpd_privacy_risk.png)

### Data Quality
![Data Quality](assets/screenshots/data_quality.png)

### Governance Control Center
![Governance Control Center](assets/screenshots/governance_control_center.png)

### Privacy Transformation Preview
![Privacy Transformation Preview](assets/screenshots/privacy_transformation_preview.png)

### How to refresh screenshots locally

```bash
uv sync --extra dev
python -m playwright install chromium
python scripts/capture_streamlit_screenshots.py
```

## Makefile Targets

- `make install`: install dependencies with `uv sync`
- `make lint`: run `ruff check src app tests`
- `make test`: run `pytest --cov=src --cov=app --cov-report=xml`
- `make pipeline`: run pipeline modules in sequence (`data_loader` -> `lgpd_classifier` -> `risk_scoring` -> `data_quality` -> `report_generator`)
- `make app`: run app with `uv run streamlit run app/main.py`
- `make screenshots`: capture screenshots with `uv run python scripts/capture_streamlit_screenshots.py`
- `make clean`: remove local caches and runtime artifacts

## Production considerations and limitations

- This is a **portfolio-grade, production-oriented** project with simulated governance controls and reproducible evidence.
- Privacy controls are **LGPD-inspired** and do not represent legal compliance certification.
- The current operational model focuses on local execution + GitHub Actions, not distributed enterprise orchestration.
- The published layer is intentionally minimized for executive consumption and does not replace full internal analytical access.

## Links

- Streamlit app: [governed-analytics-platform.streamlit.app](https://governed-analytics-platform.streamlit.app/)
- GitHub: [samuelmaia-analytics/Governed-Analytics-Platform](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform)
- technical index: [docs/README.en.md](docs/README.en.md)

## License

This work is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).

To view a copy of this license, visit:
https://creativecommons.org/licenses/by-nc/4.0/

[![License: CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc/4.0/)

