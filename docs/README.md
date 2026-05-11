# Documentação

**Language:** `PT-BR` | [EN](README.en.md)

Estrutura de documentação reorganizada para leitura rápida e manutenção:

- `docs/executive/`: narrativa executiva e resumo para recrutadores
- `docs/architecture/`: arquitetura, camada semântica e narrativa técnica
- `docs/governance/`: controles privacy-aware e documentos LGPD-inspired
- `docs/operations/`: runbooks e modelo operacional
- `docs/reports/`: relatórios gerados pelo pipeline
- `docs/legacy/`: trilha histórica numerada preservada (`00` a `10`)

## Leitura recomendada (5-10 minutos)

1. [executive/recruiter_summary.md](executive/recruiter_summary.md)
2. [architecture/architecture.md](architecture/architecture.md)
3. [governance/privacy_governance.md](governance/privacy_governance.md)
4. [architecture/semantic_layer.md](architecture/semantic_layer.md)
5. [operations/operating_model.md](operations/operating_model.md)

## Fronteiras de prontidão de produção

- Projeto de portfólio com orientação de produção.
- Dados sintéticos/públicos, sem uso de dados pessoais reais.
- Controles inspirados em LGPD, sem certificação jurídica.
- Sem IAM corporativo completo, trilha centralizada de auditoria e workflow formal de DPO.

## Índice rápido

| Área | Documento |
| --- | --- |
| Executivo | [executive/executive_summary.md](executive/executive_summary.md) |
| Caso | [executive/case_study.md](executive/case_study.md) |
| Arquitetura | [architecture/architecture.md](architecture/architecture.md) |
| API | [../src/api.py](../src/api.py) |
| Governança | [governance/privacy_governance.md](governance/privacy_governance.md) |
| Operação | [operations/release_runbook.md](operations/release_runbook.md) |
| Relatórios | [reports/data_quality_report.md](reports/data_quality_report.md) |
| Histórico | [legacy/00_planejamento.md](legacy/00_planejamento.md) |

## Architecture Decision Records (ADRs)

| ADR | Decisão |
| --- | --- |
| [ADR-001](adr/ADR-001-internal-vs-published-layer.md) | Separação entre camada interna (curated) e camada publicada |
| [ADR-002](adr/ADR-002-yaml-data-quality-contracts.md) | Contratos YAML para regras de qualidade de dados |
| [ADR-003](adr/ADR-003-lgpd-risk-before-publication.md) | Gate de risco LGPD obrigatório antes da publicação |
| [ADR-004](adr/ADR-004-streamlit-executive-governance.md) | Streamlit como interface executiva de governança |
| [ADR-005](adr/ADR-005-local-privacy-transformations.md) | Transformações de privacidade locais sem APIs externas |
