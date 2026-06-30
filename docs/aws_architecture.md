# AWS Reference Architecture

This document describes a proposed AWS architecture for the Governed Analytics
Platform. It is a reference design for portfolio review. The repository does not
create AWS resources, store credentials, or claim that this architecture is live.

Architecture image:

```text
docs/assets/governed-analytics-platform-aws-v1.png
```

## Architecture Layers

| Layer | Purpose | AWS services |
| --- | --- | --- |
| Fontes de dados | Olist CSVs, batch files, APIs and optional event streams. | S3 landing, Kinesis |
| Ingestao | Scheduled or event-driven movement into the data lake. | EventBridge, Step Functions, Glue |
| Data Lake S3 | Bronze, Silver, Gold and Quarantine zones. | S3, KMS |
| Processamento | ETL, validation, enrichment and analytical modeling. | Glue, Athena, Redshift |
| Governanca | Catalog, access control, publication gate and privacy checks. | Glue Data Catalog, Lake Formation, Macie |
| Consumo | Dashboards, APIs and query surfaces over governed data. | Athena, Redshift, App Runner, CloudFront, Route 53 |
| Observabilidade | Logs, metrics, alerts and operational traces. | CloudWatch, SNS |
| Seguranca | Least privilege, encryption and policy enforcement. | IAM, KMS, Lake Formation |
| FinOps | Cost visibility, budgets and optimization. | Trusted Advisor, Budgets, Cost Explorer, Pricing Calculator |

## Services Included

- S3
- Glue
- Glue Data Catalog
- Lake Formation
- Kinesis
- Athena
- Redshift
- Macie
- CloudWatch
- SNS
- EventBridge
- Step Functions
- App Runner
- CloudFront
- Route 53
- IAM
- KMS
- Trusted Advisor
- Budgets
- Cost Explorer
- Pricing Calculator

## Production Concerns

### Grande volume

S3 provides durable object storage for raw, standardized, governed and
quarantined data. Glue jobs can process batch workloads and Athena or Redshift
can query governed analytical layers without coupling storage and compute.

### Alta disponibilidade

The design favors managed services instead of single local servers. Services
such as S3, Glue, Athena, CloudWatch and SNS reduce operational burden and
support AWS-managed availability patterns.

### Baixa latencia

The Gold layer, Athena workgroups, Redshift marts, App Runner APIs and CloudFront
delivery reduce latency for published analytical access. The design keeps raw
and internal processing separate from executive consumption.

### Seguranca

IAM enforces least privilege, KMS protects data at rest, Lake Formation scopes
table access and Macie supports sensitive data discovery. No secrets should be
stored in Git.

### Governanca

Glue Data Catalog, Lake Formation permissions, data contracts, LGPD
classification and the Publication Gate make dataset promotion traceable and
auditable.

### Controle de custo

Budgets, Cost Explorer, Trusted Advisor, Athena workgroup limits, lifecycle
policies and Pricing Calculator estimates make cost visible before scaling the
platform.

## Portfolio Boundary

This is a proposed architecture. The implemented repository remains local and
reproducible, using sample/public data and simulated operational evidence.
