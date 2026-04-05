# Incident Runbook

## Objective

This runbook defines the minimum response flow for incidents affecting the published executive layer, semantic assets or monitoring health score.

## Incident scope

Use this runbook when one or more of the following happens:

- published layer freshness breach
- published schema drift
- duplicated published keys
- critical nulls in published columns
- semantic assets not materialized
- health score status `attention_required` or `critical`
- executive app showing missing or inconsistent published data

## Severity model

| Severity | Typical trigger | Response expectation |
| --- | --- | --- |
| `high` | freshness breach, schema drift, duplicated key, published file unavailable | immediate investigation |
| `medium` | semantic coverage degradation, KPI inconsistency, missing non-critical fields | same-day correction |
| `low` | documentation mismatch, stale derived artifact with no consumer impact | backlog with traceability |

## Detection points

- `docs/published_layer_monitoring.md`
- `data/published/monitoring/published_layer_monitoring.json`
- Streamlit health section
- CI/workflow operational artifacts

## Immediate triage

1. Confirm the latest `health_score`, failed checks and main risk in the monitoring summary.
2. Confirm whether the issue affects only the semantic assets or the base published dashboard layer.
3. Confirm whether the Streamlit app still loads and whether the issue is visible to executive consumers.
4. Confirm whether the most recent successful pipeline execution generated fresh outputs.

## Common scenarios

### Freshness breach

Symptoms:

- `published_file_freshness_hours` in `FAIL`
- health score downgraded

Actions:

1. Run `python src/run_platform_pipeline.py --steps build publish semantic monitor`
2. Confirm that the modified timestamp and monitoring summary are updated.
3. Validate whether the issue was only stale publication or also an upstream execution failure.

### Schema drift

Symptoms:

- `published_expected_schema` in `FAIL`
- app sections or BI exports break due to missing fields

Actions:

1. Compare the published file columns against `contracts/governance/privacy_governance.json`.
2. Validate whether a recent transformation changed a required field name or type.
3. Regenerate the published layer only after confirming contract compatibility.

### Semantic asset missing

Symptoms:

- semantic tab missing data
- `semantic` step failed or asset file absent

Actions:

1. Run `python src/run_platform_pipeline.py --steps publish semantic`
2. Confirm the existence of files under `data/published/semantic/`
3. Reopen the Streamlit app and verify semantic tabs

### KPI inconsistency between channels

Symptoms:

- Streamlit and Power BI show different results for the same metric

Actions:

1. Confirm which source each channel is consuming.
2. Validate `metric_catalog.md` and the published semantic assets.
3. Check whether a metric is still being calculated in app code instead of a shared mart.
4. Prioritize correction in the shared semantic layer, not only in presentation code.

## Validation checklist after recovery

- published monitoring returns expected status
- health score returns to acceptable range
- semantic assets are present and readable
- Streamlit loads without missing-data warnings
- Power BI exports remain compatible
- relevant docs or artifacts are regenerated if needed

## Communication note

Recommended stakeholder summary:

"The issue affected the governed published layer or one of its derived semantic assets. The root cause was validated, the affected artifacts were regenerated or corrected, and the executive consumption boundary is back to a healthy monitored state."
