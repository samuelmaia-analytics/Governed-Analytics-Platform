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
- A governance RAG assistant with local TF-IDF retrieval, citations and an approved-contract corpus.

The documented governance review on **24 October 2026** passed **383 tests**, including invalid Gate evidence cases. This is a historical result, not a new test run or a guarantee that all execution paths use one promotion gate.

## Architecture and publication boundary

Internal processing produces analytical candidates. Quality, contract and privacy controls provide evidence for publication decisions. Executive consumption is separated from the full internal analytical layer; governance views expose decision status and rationale.

The Gate evaluator is implemented, but enforcement differs across entrypoints. See [the technical architecture](docs/architecture/architecture.md) for the Python/dbt execution boundaries and remaining work.

Amazon S3 is part of an [AWS reference design](docs/architecture/aws_reference_architecture.md). Local folders do not represent provisioned AWS buckets.

## Generative AI for product attributes

The src/genai_feature_extraction.py module extracts category, material, compatibility, features and summaries from product descriptions with prompts and structured JSON output. Results are persisted as CSV and JSONL. The reference mode uses versioned reference data; openai calls the API when credentials are configured. The UI displays persisted results and does not run inference on page load.

## Governance RAG assistant

A separate RAG assistant answers questions grounded in approved technical contracts, using local TF-IDF retrieval, cited source excerpts and abstention when evidence is insufficient.

- **Corpus:** only three versioned contracts under contracts/, approved in a manifest and checked by SHA-256. Local-only documents, generated reports, raw data and files outside this scope are excluded.
- **Local mode:** TF-IDF is the default and needs no API key, vector database or network. Source files are revalidated for each query.
- **Optional OpenAI mode:** an external call requires explicit mode selection and consent for that query, plus server-side credentials. The integration selects supporting evidence and requires literal citations; it does not execute SQL, tools or publication decisions.
- **Limits:** external context is limited to five chunks and 7,000 characters; questions and answers are not persisted as application history.
- **Security and setup:** [RAG documentation](docs/governance_rag.md) covers sources, hashes, consent, secrets, limits, costs and the local walkthrough.

The integration review recorded on **31 October 2026** passed **1,111 tests, zero skips and 92% coverage**. This is the result from that validation, not a test run performed during this README update.

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
