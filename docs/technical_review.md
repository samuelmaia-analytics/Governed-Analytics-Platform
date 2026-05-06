# Technical Review Notes

## What is implemented

- Modular Python pipeline
- LGPD-inspired classification and privacy risk scoring
- Data quality checks and YAML-driven rules
- Publication readiness gate with explainable outputs
- Governance monitoring and decision artifacts
- Streamlit executive app for governed consumption
- Automated tests, linting, typing checks, CI/CD

## What is simulated

- Legal processes and formal DPO workflow
- Enterprise IAM and centralized audit stack
- Enterprise data catalog and approval workflow integrations

## Reviewer checklist

1. Run `uv run ruff check src app tests`
2. Run `uv run mypy src app`
3. Run `uv run pytest --cov=src --cov=app --cov-report=xml`
4. Run `streamlit run app/main.py`
5. Verify publication decision artifacts under `data/published/monitoring/`
