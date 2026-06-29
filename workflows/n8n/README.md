# n8n Automation Workflows

This folder contains importable n8n workflow definitions for the Governed Analytics Platform.

The workflows are orchestration assets only. Data processing, quality validation, LGPD classification, privacy risk scoring, documentation generation, and publication logic remain implemented in Python, SQL, dbt, and the existing project modules.

## Files

| File | Purpose |
| --- | --- |
| `governed_analytics_pipeline.json` | Main n8n workflow for running the governed analytics pipeline wrappers. |
| `governed_analytics_error_handler.json` | Reusable error-handling workflow that records failed executions through the pipeline log script. |

## Expected runtime

Run n8n on a machine that has:

- Python 3.11+
- project dependencies installed
- access to this repository checkout
- `PROJECT_ROOT_DIR` pointing to the repository root, when n8n is not started from the repository directory

Example command used by the workflow nodes:

```bash
python scripts/run_governance_pipeline.py --config config/pipeline_config.yml
```

If the project is managed through `uv`, the command can be adapted inside n8n to:

```bash
uv run python scripts/run_governance_pipeline.py --config config/pipeline_config.yml
```

## Import

1. Open n8n.
2. Go to **Workflows**.
3. Choose **Import from File**.
4. Import `governed_analytics_pipeline.json`.
5. Import `governed_analytics_error_handler.json`.
6. Review command paths and environment variables before activating scheduled runs.

## Scope

This automation layer does not replace GitHub Actions or Streamlit deployment. It is intended for local or self-hosted orchestration, portfolio demonstration, operational scheduling, and alert-friendly logging.
