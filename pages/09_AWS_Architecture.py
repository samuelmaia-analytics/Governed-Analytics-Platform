from __future__ import annotations

import pandas as pd
import streamlit as st

from streamlit_shared import PROJECT_ROOT, relative_path, render_artifact_diagnostics

ARCHITECTURE_IMAGE_PATH = (
    PROJECT_ROOT / "docs/assets/governed-analytics-platform-aws-v1.png"
)

LAYERS = [
    {
        "layer": "Fontes de dados",
        "description": "Olist CSVs, batch files, APIs and optional event streams.",
        "services": "S3 landing, Kinesis",
    },
    {
        "layer": "Ingestão",
        "description": "Scheduled or event-driven ingestion into controlled landing zones.",
        "services": "EventBridge, Step Functions, Glue",
    },
    {
        "layer": "Data Lake S3",
        "description": "Bronze, Silver, Gold and Quarantine zones with lifecycle policies.",
        "services": "S3, KMS",
    },
    {
        "layer": "Processamento",
        "description": "ETL, validation, enrichment and analytical modeling.",
        "services": "Glue, Athena, Redshift",
    },
    {
        "layer": "Governança",
        "description": "Catalog, access control, publication gate and privacy checks.",
        "services": "Glue Data Catalog, Lake Formation, Macie",
    },
    {
        "layer": "Consumo",
        "description": "Dashboards, APIs and analytical query surfaces over governed data.",
        "services": "Athena, Redshift, App Runner, CloudFront, Route 53",
    },
    {
        "layer": "Observabilidade",
        "description": "Pipeline logs, metrics, alerts and operational traces.",
        "services": "CloudWatch, SNS",
    },
    {
        "layer": "Segurança",
        "description": "Least privilege, encryption, private access and key management.",
        "services": "IAM, KMS, Lake Formation",
    },
    {
        "layer": "FinOps",
        "description": "Budgets, anomaly review, query limits and cost visibility.",
        "services": "Trusted Advisor, Budgets, Cost Explorer, Pricing Calculator",
    },
]

SERVICES = [
    "S3",
    "Glue",
    "Glue Data Catalog",
    "Lake Formation",
    "Kinesis",
    "Athena",
    "Redshift",
    "Macie",
    "CloudWatch",
    "SNS",
    "EventBridge",
    "Step Functions",
    "App Runner",
    "CloudFront",
    "Route 53",
    "IAM",
    "KMS",
    "Trusted Advisor",
    "Budgets",
    "Cost Explorer",
    "Pricing Calculator",
]

GUARANTEES = [
    {
        "capability": "Grande volume",
        "approach": "S3 separates storage from compute, Glue processes batch workloads, and Redshift/Athena serve analytical access.",
    },
    {
        "capability": "Alta disponibilidade",
        "approach": "Managed AWS services reduce single-host dependency and support multi-AZ control planes where applicable.",
    },
    {
        "capability": "Baixa latencia",
        "approach": "Published Gold datasets, Athena workgroups, Redshift marts, CloudFront and App Runner reduce serving latency.",
    },
    {
        "capability": "Segurança",
        "approach": "IAM least privilege, KMS encryption, Lake Formation permissions and Macie discovery protect sensitive data.",
    },
    {
        "capability": "Governança",
        "approach": "Glue Catalog, contracts, publication gate and LGPD checks make promotion decisions auditable.",
    },
    {
        "capability": "Controle de custo",
        "approach": "Budgets, Cost Explorer, Trusted Advisor, query limits and lifecycle policies keep spend visible.",
    },
]

st.title("AWS Reference Architecture")
st.caption(
    "Reference architecture for a governed analytics platform on AWS. "
    "This is a portfolio design, not evidence of provisioned cloud resources."
)

if ARCHITECTURE_IMAGE_PATH.exists():
    st.image(
        str(ARCHITECTURE_IMAGE_PATH),
        caption=f"Source: {relative_path(ARCHITECTURE_IMAGE_PATH)}",
        width="stretch",
    )
else:
    st.warning(
        f"Architecture image not found at `{relative_path(ARCHITECTURE_IMAGE_PATH)}`. "
        "Insert the diagram PNG in this path to render it here."
    )

st.subheader("Architecture layers")
st.dataframe(pd.DataFrame(LAYERS), width="stretch", hide_index=True)

st.subheader("AWS services used in the reference design")
service_columns = st.columns(3)
for index, service in enumerate(SERVICES):
    service_columns[index % 3].markdown(f"- `{service}`")

st.subheader("How the architecture addresses production concerns")
st.dataframe(pd.DataFrame(GUARANTEES), width="stretch", hide_index=True)

st.info(
    "No credentials, buckets, endpoints or live AWS resources are created by this repository. "
    "The page documents a deployable direction for technical review."
)

render_artifact_diagnostics()
