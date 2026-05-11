# Documentation Index

**Language:** `EN` | [PT-BR](README.md)

Documentation layout was reorganized for faster technical review:

- `docs/executive/`: executive story and recruiter-facing summaries
- `docs/architecture/`: architecture and semantic model rationale
- `docs/governance/`: LGPD-inspired and privacy-aware governance controls
- `docs/operations/`: runbooks and operating model
- `docs/reports/`: generated operational/governance reports
- `docs/legacy/`: preserved historical numbered track (`00` to `10`)

## Recommended review path (5-10 minutes)

1. [executive/recruiter_summary.md](executive/recruiter_summary.md)
2. [architecture/architecture.md](architecture/architecture.md)
3. [governance/privacy_governance.md](governance/privacy_governance.md)
4. [architecture/semantic_layer.md](architecture/semantic_layer.md)
5. [operations/operating_model.md](operations/operating_model.md)

## Production readiness boundaries

- Production-inspired portfolio implementation.
- Uses synthetic/sample/public data only.
- LGPD-inspired governance controls, not legal compliance certification.
- No enterprise IAM, centralized audit logging, formal DPO workflow, or real DPA processing agreement.

## Quick index

| Area | Document |
| --- | --- |
| Executive | [executive/executive_summary.md](executive/executive_summary.md) |
| Case Study | [executive/case_study.md](executive/case_study.md) |
| Architecture | [architecture/architecture.md](architecture/architecture.md) |
| API | [../src/api.py](../src/api.py) |
| Governance | [governance/privacy_governance.md](governance/privacy_governance.md) |
| Operations | [operations/release_runbook.md](operations/release_runbook.md) |
| Reports | [reports/data_quality_report.md](reports/data_quality_report.md) |
| Legacy | [legacy/00_planejamento.md](legacy/00_planejamento.md) |
