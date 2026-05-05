# Data Governance Operating Model (Portfolio Version)

## Purpose

Define how governance controls are operationalized in this project.
This model is production-oriented for portfolio demonstration.

## Roles (simulated)

| Role | Responsibility |
| --- | --- |
| Analytics Engineer | implement pipeline, quality checks, publication controls |
| Data Governance Analyst | review privacy classification and risk rationale |
| Product/Business Stakeholder | validate executive metrics and publication needs |
| Security/Privacy Reviewer | validate control design and residual risks |

## Control Lifecycle

1. **Classify**: classify columns by sensitivity.
2. **Assess**: compute privacy risk score.
3. **Validate**: run data quality and governance checks.
4. **Decide**: determine publication status.
5. **Evidence**: store reports and artifacts.
6. **Monitor**: track published layer health and governance trends.

## Decision States

- `Approved`: low privacy risk and no blocking quality failure.
- `Needs Review`: medium risk and/or quality failures that require remediation.
- `Blocked`: high privacy risk or critical governance failure.

## Inputs

- `contracts/governance/privacy_governance.json`
- `contracts/governance/lgpd_classification_rules.yml`
- `contracts/data_quality_rules.yml`

## Outputs

- privacy/governance report in `docs/`
- data quality report in `docs/`
- semantic layer documentation
- published monitoring artifacts in `data/published/monitoring/`

## Implemented vs Simulated

Implemented:
- technical controls and decision logic in code;
- quality and privacy evidence generation.

Simulated:
- legal metadata and formal compliance governance flow;
- enterprise IAM and external audit platform integration.

## Recommended Next Steps for Real Production

- formal data access matrix by role/environment;
- centralized audit logging;
- legal/compliance review workflow;
- incident response and SLA definitions for governance failures.
