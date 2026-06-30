# AWS Reference Architecture

This document describes the target AWS architecture for the Governed Analytics
Platform. It is a reference design only: the repository does not provision cloud
resources, store credentials, or claim that AWS workloads are currently running.

The machine-readable source is `config/aws_reference_architecture.yml`.

## Target Mapping

| Capability | AWS target | Local implementation in this repository |
| --- | --- | --- |
| Data Lake storage | Amazon S3 | `data/raw`, `data/standardized`, `data/curated`, `data/published`, `data/quarantine` |
| Metadata catalog | AWS Glue Data Catalog | `contracts/catalog`, `data/curated/catalog` |
| Processing | AWS Glue or Amazon ECS Fargate | `src/`, `scripts/`, `dbt/` |
| SQL query layer | Amazon Athena | DuckDB engine and versioned SQL files |
| Orchestration | EventBridge and Step Functions | n8n workflow templates and local scripts |
| Observability | Amazon CloudWatch | `logs/` and `data/published/monitoring/` |

## Security And Governance Controls

The target architecture assumes:

- S3 block public access and encryption on all buckets.
- IAM roles scoped by layer and workload responsibility.
- Published-layer-only access for executive consumption.
- Glue catalog tags for owner, environment, cost center, and data classification.
- Manual approval or explicit policy gate before publication.
- Operational logs retained with defined lifecycle rules.

## Cost Controls

Minimum controls for a real AWS deployment:

1. Configure AWS Budgets for each account and alert at 50, 80, and 100 percent.
2. Use Athena workgroup bytes-scanned limits.
3. Partition published datasets before broad query access.
4. Apply S3 lifecycle policies for raw, quarantine, and generated query outputs.
5. Prefer serverless or scheduled compute over always-on clusters.
6. Set log retention windows in CloudWatch.
7. Require tags: `project`, `environment`, `owner`, `cost_center`, and `data_classification`.

## Portfolio Boundary

This architecture is intentionally documented as a deployable direction, not as
current production infrastructure. The implemented project remains local and
reproducible, with cloud mapping used to show how the same governance controls
would translate to AWS.
