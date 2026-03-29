# Documentação do Projeto

Este diretório concentra a documentação principal do case. A navegação abaixo foi reorganizada para leitura rápida por avaliador e para manutenção do projeto.

## Comece Por Objetivo

- leitura executiva: [executive_summary.md](executive_summary.md)
- defesa técnica: [case_answers.md](case_answers.md)
- operação e governança: [operating_model.md](operating_model.md)
- apresentação final: [10_apresentacao_final.md](10_apresentacao_final.md)

## Ordem recomendada

1. [00_planejamento.md](00_planejamento.md)
2. [01_contexto.md](01_contexto.md)
3. [02_carga_e_modelagem.md](02_carga_e_modelagem.md)
4. [03_catalogacao.md](03_catalogacao.md)
5. [04_analises_sql.md](04_analises_sql.md)
6. [05_dashboard.md](05_dashboard.md)
7. [06_arquitetura_proposta.md](06_arquitetura_proposta.md)
8. [07_bonus_genai_dataapps.md](07_bonus_genai_dataapps.md)
9. [08_pipelines.md](08_pipelines.md)
10. [09_genai_llm_processar.md](09_genai_llm_processar.md)
11. [10_apresentacao_final.md](10_apresentacao_final.md)

## Guias centrais

- [executive_summary.md](executive_summary.md): visão executiva única para banca, entrevista e revisão rápida
- [case_answers.md](case_answers.md): narrativa principal do case
- [architecture.md](architecture.md): arquitetura implementada
- [operating_model.md](operating_model.md): visão única de pipeline, governança, publicação e consumo
- [collection_catalog.md](collection_catalog.md): coleção local e inventário catalogável
- [dadosfera_evidencias.md](dadosfera_evidencias.md): links e evidências publicadas
- [dadosfera_api_sync.md](dadosfera_api_sync.md): sincronização de catálogo via API
- [dadosfera_native_pipeline_runbook.md](dadosfera_native_pipeline_runbook.md): operação de pipeline nativo via API
- [privacy_governance.md](privacy_governance.md): decisões de minimização e publicação
- [governance_policy.md](governance_policy.md): governança, retenção e responsabilidades
- [engineering_governance.md](engineering_governance.md): guardrails de CI, ownership e contribuição
- [branch_protection_recommendation.md](branch_protection_recommendation.md): configuração recomendada no GitHub para merge e deploy

## Trilhas por Perfil

- avaliador de negócio: [executive_summary.md](executive_summary.md), [05_dashboard.md](05_dashboard.md), [dadosfera_evidencias.md](dadosfera_evidencias.md)
- avaliador técnico: [case_answers.md](case_answers.md), [02_carga_e_modelagem.md](02_carga_e_modelagem.md), [architecture.md](architecture.md), [schema_contract_report.md](schema_contract_report.md)
- operação e plataforma: [operating_model.md](operating_model.md), [release_runbook.md](release_runbook.md), [rollback_runbook.md](rollback_runbook.md), [dadosfera_native_pipeline_runbook.md](dadosfera_native_pipeline_runbook.md), [engineering_governance.md](engineering_governance.md)

## Relatórios gerados pelo pipeline

- [raw_data_inventory.md](raw_data_inventory.md)
- [eda_summary.md](eda_summary.md)
- [fact_orders_enriched.md](fact_orders_enriched.md)
- [data_quality_report.md](data_quality_report.md)
- [schema_contract_report.md](schema_contract_report.md)
- [data_classification.md](data_classification.md)
- [published_layer_monitoring.md](published_layer_monitoring.md)
- [semantic_layer.md](semantic_layer.md)
- [operational_job_report.md](operational_job_report.md)

## Operação e evidências

- [dadosfera_capture_runbook.md](dadosfera_capture_runbook.md)
- [streamlit_capture_runbook.md](streamlit_capture_runbook.md)
- [release_runbook.md](release_runbook.md)
- [rollback_runbook.md](rollback_runbook.md)
- [final_pre_delivery_audit.md](final_pre_delivery_audit.md)
- [case_delivery_checklist.md](case_delivery_checklist.md)

## Complementos

- [bi_bonus.md](bi_bonus.md)
- [genai_bonus.md](genai_bonus.md)
- [about_dadosfera.md](about_dadosfera.md)

## Critério de Navegação

Se o objetivo for entender rapidamente o valor entregue, não comece pela ordem cronológica dos arquivos `00` a `10`. A ordem cronológica ajuda a reconstruir a evolução do case, mas os guias centrais e as trilhas por perfil foram organizados para acelerar avaliação, entrevista e handoff.
