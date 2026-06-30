# AWS Cost Estimation

This document explains the cost-governance mindset for the proposed AWS
reference architecture. It is a portfolio estimate guide, not a billing report
and not a claim that AWS resources are currently provisioned.

## Objective

The objective is to show how a governed analytics platform should be reviewed
before deployment from a cost, budget and FinOps perspective. The estimate helps
identify high-impact services, control levers and operational risks.

## Services With Higher Cost Impact

- **Redshift**: can become expensive when clusters are always on or oversized.
- **Glue**: cost grows with DPU usage, job duration and frequency.
- **Athena**: cost grows with bytes scanned, especially without partitioning.
- **S3**: cost grows with storage volume, request patterns and retained versions.
- **CloudWatch**: logs and metrics can become expensive with high retention.
- **Kinesis**: cost depends on stream/shard throughput and retention.
- **Data transfer and CloudFront**: relevant when dashboards or APIs serve broad traffic.

## Cost Reduction Strategies

- Partition data before broad Athena access.
- Store published analytics in columnar formats such as Parquet.
- Use S3 lifecycle policies for raw, quarantine, temporary and query-result data.
- Prefer serverless or scheduled workloads when usage is intermittent.
- Right-size Glue jobs and avoid unnecessary reruns.
- Avoid always-on Redshift for low or sporadic analytical demand.
- Set CloudWatch retention windows.
- Tag resources by project, environment, owner, cost center and data classification.
- Review monthly costs and anomalies.

## Athena vs Redshift

Use **Athena** when:

- workloads are ad hoc or intermittent;
- data already lives in S3;
- latency requirements are moderate;
- cost control is easier through bytes-scanned limits.

Use **Redshift** when:

- workloads are frequent and performance-sensitive;
- teams need governed marts with predictable query latency;
- concurrency and BI consumption justify a warehouse;
- data modeling and workload management are mature enough.

## Glue vs EMR

Use **Glue** when:

- batch ETL jobs are moderate and scheduled;
- serverless execution is preferred;
- operational overhead should stay low;
- jobs can be expressed through Spark, Python or Glue workflows.

Use **EMR** when:

- workloads require fine-grained cluster control;
- processing volume is very high or specialized;
- custom big-data frameworks are required;
- the team can operate and optimize clusters responsibly.

## CloudWatch Log Retention

CloudWatch logs should not be retained indefinitely by default. Suggested policy:

- development logs: 7 to 14 days;
- staging logs: 30 days;
- production operational logs: 90 days or according to compliance needs;
- exported audit evidence: store in S3 with lifecycle and access controls.

## S3 Lifecycle Policies

Recommended lifecycle controls:

- transition raw historical files to cheaper storage classes;
- expire temporary query outputs;
- review quarantine retention separately because it may contain rejected records;
- retain published evidence long enough for audit and portfolio review;
- avoid storing duplicate CSV and Parquet outputs unless needed.

## AWS Budgets

Create budgets by account/environment and configure alerts at:

- 50 percent: early visibility;
- 80 percent: operational warning;
- 100 percent: hard escalation.

For this project, the key portfolio recommendation is an **80 percent budget
alert** routed to an operational channel before spend reaches the monthly limit.

## AWS Cost Explorer

Use Cost Explorer monthly to inspect:

- service-level spend;
- daily trends;
- tag-based allocation;
- unexpected spikes;
- usage patterns by environment.

## AWS Trusted Advisor

Trusted Advisor can help identify:

- idle or underused resources;
- cost optimization opportunities;
- security gaps;
- service limit risks;
- reliability recommendations.

## AWS Pricing Calculator

Before provisioning, use Pricing Calculator to model:

- S3 storage and requests;
- Glue job frequency and DPU-hours;
- Athena scanned bytes;
- Redshift sizing;
- CloudWatch logs and metrics;
- data transfer and CloudFront usage.

## Real-World Cost Risks

- Leaving Redshift or EMR resources running when not needed.
- Athena scans over unpartitioned CSV data.
- Excessive CloudWatch log retention.
- Multiple environments duplicating the same data.
- Unbounded Kinesis retention or throughput.
- Query-result files accumulating in S3.
- Missing tags that prevent cost allocation.

## Limitations

This document does not calculate a real monthly bill because the repository does
not provision AWS resources. Actual cost depends on data volume, query frequency,
retention, region, service configuration, concurrency and traffic patterns.
