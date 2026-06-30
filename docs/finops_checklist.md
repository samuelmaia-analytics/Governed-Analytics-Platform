# FinOps Checklist

Use this checklist before promoting the reference architecture to a real AWS
environment.

| Check | Status |
| --- | --- |
| Monthly AWS budget configured by environment. | Pending for real deployment |
| Budget alert configured at 80 percent. | Pending for real deployment |
| Cost tags defined: `project`, `environment`, `owner`, `cost_center`, `data_classification`. | Proposed |
| Cost tags enforced during provisioning. | Pending for real deployment |
| CloudWatch log retention configured. | Pending for real deployment |
| S3 lifecycle policies configured for raw, quarantine, temporary and published outputs. | Pending for real deployment |
| Serverless services used when possible. | Proposed |
| Unused resources scheduled for shutdown or removal. | Pending for real deployment |
| SNS alerts configured for budget and pipeline incidents. | Pending for real deployment |
| Monthly cost review with Cost Explorer. | Pending for real deployment |
| Trusted Advisor reviewed for cost optimization. | Pending for real deployment |
| Athena workgroup scan limits configured. | Pending for real deployment |
| Redshift usage justified by latency and concurrency needs. | Pending for real deployment |
| Pricing Calculator estimate reviewed before provisioning. | Pending for real deployment |

## Review Cadence

- Review budgets and cost anomalies weekly during active development.
- Review service-level spend monthly.
- Revisit architecture choices whenever data volume, query concurrency or SLA
  expectations change.
