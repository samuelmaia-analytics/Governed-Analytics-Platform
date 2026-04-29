# Documentação

[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live-red?logo=streamlit)](https://governed-analytics-platform.streamlit.app/)
[![Language](https://img.shields.io/badge/Language-PT--BR-0A66C2)](../README.md)

**Language:** `PT-BR` | [EN](README.en.md)

Índice técnico da pasta `docs/`. Contexto geral, setup e execução local ficam no [README da raiz](../README.md).

## Comece por aqui

1. [executive_summary.md](executive_summary.md)
2. [architecture.md](architecture.md)
3. [operating_model.md](operating_model.md)
4. [privacy_governance.md](privacy_governance.md)
5. [technical_narrative.md](technical_narrative.md)

## Guias principais (válidos no repositório)

- [executive_summary.md](executive_summary.md): visão executiva
- [architecture.md](architecture.md): arquitetura implementada
- [operating_model.md](operating_model.md): pipeline, publicação, deploy e operação
- [privacy_governance.md](privacy_governance.md): fronteira de exposição, LGPD e checks da camada publicada
- [engineering_governance.md](engineering_governance.md): guardrails do repositório e workflows
- [platform_publication.md](platform_publication.md): publicação em ambiente de plataforma
- [technical_narrative.md](technical_narrative.md): defesa técnica consolidada

## Relatórios gerados

- [raw_data_inventory.md](raw_data_inventory.md)
- [eda_summary.md](eda_summary.md)
- [fact_orders_enriched.md](fact_orders_enriched.md)
- [data_quality_report.md](data_quality_report.md)
- [schema_contract_report.md](schema_contract_report.md)
- [data_classification.md](data_classification.md)
- [published_layer_monitoring.md](published_layer_monitoring.md)
- [semantic_layer.md](semantic_layer.md)
- [operational_job_report.md](operational_job_report.md)
- [technical_lineage.md](technical_lineage.md)
- [governance_scorecards.md](governance_scorecards.md)

## Camada semântica e lineage

- o pipeline Python continua produzindo `fact_orders_enriched` e `fact_orders_dashboard`
- o dbt entra depois desses ativos para documentação, testes, lineage e marts reutilizáveis
- Streamlit, Power BI e workflows SQL devem ser lidos a partir da camada publicada e dos marts semânticos

## Runbooks e operação

- [release_runbook.md](release_runbook.md)
- [rollback_runbook.md](rollback_runbook.md)
- [publication_checklist.md](publication_checklist.md)
- [streamlit_capture_runbook.md](streamlit_capture_runbook.md)

## Materiais complementares

- [collection_catalog.md](collection_catalog.md)
- [governance_policy.md](governance_policy.md)
- [privacy_governance.md](privacy_governance.md)
- [branch_protection_recommendation.md](branch_protection_recommendation.md)
- [bi_bonus.md](bi_bonus.md)
- [genai_bonus.md](genai_bonus.md)

## Histórico

Os arquivos numerados `00` a `10` foram mantidos como trilha histórica do projeto e podem ser usados como narrativa de evolução.
