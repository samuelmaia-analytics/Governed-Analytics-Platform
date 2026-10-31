# Governed Analytics Platform

**Language:** `English` · [Português (Brasil)](README.md)

[![CI](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/ci.yml)
[![Lint](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform/actions/workflows/lint.yml)
[![License](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](LICENSE)

A personal portfolio platform that turns public Olist e-commerce data into analytical assets with quality checks, privacy classification, contracts, lineage and publication decision evidence.

[Open the demonstration](https://governed-analytics-platform.streamlit.app/)

## Capabilities and evidence

- Python and SQL ingestion, transformation and analytical modeling.
- dbt + DuckDB staging, intermediate and marts models, executed independently of the Python orchestration entrypoint.
- Data Contracts, Data Quality, Data Lineage and explainable Privacy Risk Score.
- A deterministic Publication Gate evaluator with `Approved`, `Needs Review` and `Blocked` decisions, used by the Governance Control Center.
- Streamlit executive views, FastAPI endpoints, operational artifacts and GitHub Actions checks.
- Optional Snowflake integration and versioned n8n workflow templates.

The documented governance review on **24 October 2026** passed **383 tests**, including invalid Gate evidence cases. This is a historical result, not a new test run or a guarantee that all execution paths use one promotion gate.

## Architecture and publication boundary

Internal processing produces analytical candidates. Quality, contract and privacy controls provide evidence for publication decisions. Executive consumption is separated from the full internal analytical layer; governance views expose decision status and rationale.

The Gate evaluator is implemented, but enforcement differs across entrypoints. See [the technical architecture](docs/architecture/architecture.md) for the Python/dbt execution boundaries and remaining work.

Amazon S3 is part of an [AWS reference design](docs/architecture/aws_reference_architecture.md). Local folders do not represent provisioned AWS buckets.

## Generative AI for product attributes

A Python module extracts category, material, compatibility, features and summaries from product descriptions using prompts and structured JSON output. It persists CSV/JSONL artifacts. The `reference` mode uses versioned reference output; `openai` calls the OpenAI API when credentials are configured. The UI displays persisted results and does not run inference on page load. This feature extraction implementation does not include RAG.

[Module](src/genai_feature_extraction.py) · [Documentation](docs/genai_bonus.md)

## Run locally

Requires Python 3.11 or later. From the repository root on Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
make test
make app
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and copy the environment file with `copy .env.example .env`.

## Documentation

- [Architecture](docs/architecture/architecture.md)
- [dbt modeling](dbt/README.md)
- [Documentation index](docs/README.en.md)
- [Access and retention policy](docs/governance/access_and_retention_policy.md)
- [Detailed project overview in Portuguese](README.md)

## Scope

Production-inspired portfolio work using public, sample or synthetic data. Legal roles and governance context are demonstrative; enterprise IAM and centralized audit are not fully implemented. AWS is a proposed design. This project does not constitute legal certification of LGPD compliance.

## Author

**Samuel de Andrade Maia — Data Engineer (Pleno) | Analytics Engineer**

Data Engineering at **Avanade** since **20 October 2026**. This personal portfolio project does not represent work, data or results delivered for Avanade or its clients.

[LinkedIn](https://www.linkedin.com/in/samuelmaia-analytics/) · [Portfolio](https://samuelmaia-analytics.github.io/samuelmaia-analytics/)

## License

**Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**. See [LICENSE](LICENSE) and the [dashboard notice](DASHBOARD_LICENSE_NOTICE.txt).
