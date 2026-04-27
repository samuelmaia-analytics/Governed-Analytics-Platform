# Governed Analytics Platform

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/ci.yml)
[![Lint](https://img.shields.io/badge/Lint-Ruff-2D2D2D?logo=ruff&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/lint.yml)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live-red?logo=streamlit)](https://governed-analytics-platform.streamlit.app/)
[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform)

**Language:** [PT-BR](README.md) | `EN`

A Streamlit analytics platform that demonstrates Data Governance, LGPD classification, Data Quality, automated EDA, and executive reporting.

## Business Problem

Analytics teams often accelerate delivery without formal controls for quality, privacy, and traceability. This creates regulatory risk, low trust in data assets, and weak governance for executive decisions.

## Solution

The project implements a governed analytics product approach:

- explicit boundary between internal and published layers;
- column-level LGPD classification with privacy risk scoring;
- reusable data quality checks;
- automated EDA for analytical acceleration;
- Markdown reports for technical and executive governance.

## Core Features

- Executive Overview with governance KPIs.
- Data Catalog with metadata and column dictionary.
- LGPD & Privacy Risk with recommendations.
- Data Quality checks with severity and status.
- EDA (descriptive stats, null profile, outliers, correlation).
- Governance Report generated in `docs/`.

## Main Structure

| Path | Purpose |
| --- | --- |
| `app/` | modern executive Streamlit app |
| `streamlit_app/` | legacy app preserved for compatibility |
| `src/` | analytics engineering and governance modules |
| `data/samples/` | synthetic demonstration dataset |
| `docs/` | governance reports and technical docs |
| `tests/` | automated test suite |

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

New app:

```bash
streamlit run app/main.py
```

Legacy app:

```bash
streamlit run streamlit_app/app.py
```

## Testing and Quality Gates

```bash
ruff check src streamlit_app app tests
python -m mypy src/data_loader.py src/data_quality.py src/eda.py src/lgpd_classifier.py src/risk_scoring.py src/report_generator.py src/governance_types.py app/main.py app/context.py app/components/cards.py app/pages/data_catalog.py app/pages/data_quality.py app/pages/eda.py app/pages/executive_overview.py app/pages/governance_report.py app/pages/lgpd_privacy_risk.py
pytest --cov=src --cov=streamlit_app --cov-report=term-missing
```

## Links

- Streamlit app: [governed-analytics-platform.streamlit.app](https://governed-analytics-platform.streamlit.app/)
- GitHub: [samuelmaia-analytics/Governed-Analytics-Platform](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform)
