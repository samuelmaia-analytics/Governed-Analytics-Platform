# Architecture: Governed Analytics Platform

## 1) Overview

The Governed Analytics Platform is a **production-inspired governed analytics project** designed to demonstrate Analytics Engineering and Data Governance patterns end to end.

The architecture focuses on:

- explicit separation between internal analytical processing and published executive consumption;
- privacy-aware controls (LGPD-inspired classification and risk scoring);
- quality and contract validation before publication;
- reproducible governance evidence for reviewers and technical stakeholders.

It is intentionally scoped as a portfolio implementation, with transparent boundaries between implemented controls and simulated enterprise context.

## 2) Logical architecture

The platform is composed of the following major components:

1. **Data ingestion/loading**
   - loads source data (sample/public datasets) into the pipeline entrypoint.

2. **Profiling**
   - derives exploratory and structural context (null patterns, distributions, basic diagnostics).

3. **LGPD/privacy classification**
   - classifies columns by privacy sensitivity using heuristics, regex, and contract overrides.

4. **Data quality rules**
   - executes rule-based checks (completeness, consistency, domain checks, publication-critical checks).

5. **Risk scoring**
   - computes explainable privacy risk level and recommendation signals.

6. **Data contracts**
   - validates schema/governance expectations (required/forbidden fields, quality contracts).

7. **Publication layer**
   - materializes a minimized/pseudonymized output surface for executive consumption.

8. **Governance scorecards**
   - summarizes governance status and control outcomes for reporting.

9. **Monitoring history**
   - appends governance snapshots and publication-state history over time.

10. **Technical lineage**
    - documents transformation and asset dependencies for traceability.

11. **Streamlit executive app**
    - presents governance KPIs, risk rationale, and publication decision context.

12. **FastAPI governance endpoint**
    - exposes publication/governance status for external consumers and integration.

13. **CI/CD workflows**
    - enforces lint, tests, and coverage gates for repository reliability.

## 3) Data flow

High-level flow from raw/sample input to published outputs:

1. Source datasets are ingested from `data/raw/landing/` and sample/public inputs.
2. Data is prepared and transformed into analytical assets in curated layers.
3. Profiling and quality checks generate diagnostics and evidence.
4. Privacy classification and risk scoring evaluate exposure risk.
5. Contracts validate publication constraints (required/forbidden/pseudonymized expectations).
6. Publication process writes controlled outputs to `data/published/dashboard/` and semantic/monitoring artifacts.
7. Executive app and reports consume published artifacts, not full internal detail.

## 4) Governance flow

Governance is enforced through a layered control sequence:

1. **Classification**: each column receives a sensitivity class and action orientation.
2. **Quality checks**: rules detect data reliability issues that may affect publication.
3. **Contract validation**: schema and governance rules verify publication eligibility constraints.
4. **Risk scoring**: privacy exposure is quantified and translated into operational recommendation.
5. **Decision support**: governance outputs are consolidated into publication status and evidence.

This flow ensures publication decisions are not based on visualization readiness alone, but on explicit privacy + quality + contract controls.

## 5) Publication flow

Datasets move through explicit publication states:

- **Candidate**
  - dataset is generated and ready for governance evaluation.

- **Validated**
  - required validation routines ran successfully (checks executed, evidence produced).

- **Needs Review**
  - medium privacy risk and/or quality/control findings require remediation review.

- **Approved**
  - controls indicate acceptable publication conditions for executive exposure.

- **Blocked**
  - high privacy risk or critical governance/quality contract failure prevents publication.

These states support auditable and explainable publication governance.

## 6) Component responsibilities

| Component | Path | Responsibility | Output |
| --- | --- | --- | --- |
| Ingestion/Loading | `src/data_loader.py`, `src/ingest.py` | Load and validate source/sample datasets | initial dataframe/assets |
| Profiling/EDA | `src/eda.py` | Generate exploratory and structural diagnostics | EDA summaries/reports |
| LGPD Classification | `src/lgpd_classifier.py`, `contracts/governance/lgpd_classification_rules.yml` | Classify columns by sensitivity (heuristic + contract) | classification dataframe |
| Data Quality Rules | `src/data_quality.py`, `src/data_quality_rules.py`, `contracts/data_quality_rules.yml` | Execute quality checks and rule validations | quality results/tables |
| Privacy Risk Scoring | `src/risk_scoring.py` | Compute explainable risk score and level | risk score + recommendations |
| Contract Validation | `src/schema_contracts.py`, `contracts/` | Enforce schema and governance contract expectations | contract validation results |
| Publication Layer | `src/publish_dashboard.py`, `src/platform_publication.py` | Build controlled published datasets | `data/published/dashboard/*` |
| Governance Scorecards | `src/governance_scorecards.py` | Materialize governance summary artifacts | scorecards (`csv/json`) |
| Monitoring History | `src/governance_history.py`, `src/published_monitoring.py` | Persist historical governance/publication snapshots | monitoring + history files |
| Technical Lineage | `src/lineage.py`, `docs/technical_lineage.md` | Track transformation lineage and dependencies | lineage artifacts |
| Executive App | `app/main.py`, `app/pages/*` | Present governance and publication decision views | Streamlit UI |
| FastAPI Endpoint | `src/api.py` | Serve governance/publication status over HTTP (`/api/v1/governance/status`) | JSON API response |
| CI/CD Workflows | `.github/workflows/*` | Enforce lint/test/coverage and governance checks | CI validation status |

## 7) Production readiness boundaries

### Production-inspired elements

- layered data architecture and publication boundary;
- explicit governance control chain (classification, quality, contracts, risk);
- reproducible artifacts and decision evidence;
- CI quality gates and documentation of operations.

### Simulated or constrained scope

- legal/governance metadata includes fictional entities for demonstration;
- no real personal data processing is intended in this portfolio context;
- enterprise IAM, SOC controls, and centralized audit platforms are not fully implemented here;
- this repository is not positioned as a live enterprise production platform.

The goal is technical rigor and transparency, not overclaiming production certification.

## 8) Future architecture improvements

1. **dbt layer**
   - add modeled transformation layer with explicit tests and semantic model governance.

2. **Stronger metadata catalog**
   - expand metadata management beyond local artifacts, with richer ownership and SLA metadata.

3. **More historical observability**
   - persist long-range governance telemetry for trend analysis and control drift detection.

4. **Automated publication gate**
   - formalize a deterministic gate that blocks promotion unless all control thresholds pass.

5. **Stronger security checks**
   - add policy-as-code checks for secrets exposure, access control assumptions, and artifact hardening.

---

This architecture is designed to be understandable by senior data engineering reviewers while keeping claims aligned with portfolio scope.
