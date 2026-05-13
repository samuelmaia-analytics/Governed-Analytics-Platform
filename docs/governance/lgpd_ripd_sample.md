# Mini RIPD (LGPD-inspired)

> Documento simulado para portfólio. Não substitui avaliação jurídica formal.

- Data de geração: **2026-05-11**
- Dataset avaliado: **fact_orders_dashboard**
- Risco de privacidade: **high (100/100)**
- Falhas de qualidade: **5**

## Inventário de Tratamento (simulado)

- Finalidade: Executive performance and governance monitoring
- Base legal: legitimate_interest (simulated)
- Controlador: Olist Governed Analytics (fictitious)
- Operador: Analytics Platform Team (fictitious)
- Encarregado (DPO): dpo@example.org (fictitious)
- Retenção: 12 months in published layer, 24 months in curated internal layer (simulated)

## Matriz de Risco

| risk_id | risk_event | probability | impact | severity | mitigation | evidence |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Leakage of direct or sensitive identifiers | Medium | High | Critical | Pseudonymize/remove sensitive fields before publication. | Classification inventory and publication checks. |
| R2 | Re-identification through quasi-identifiers | Medium | Medium | Medium | Data minimization and aggregation in published layer. | Published schema and forbidden-columns validation. |
| R3 | Publication with unresolved quality issues | High | Medium | High | Block/review publication when quality checks fail. | Failed checks count: 5. |
| R4 | Missing legal and retention metadata | Medium | Medium | Medium | Maintain processing inventory and LGPD-inspired RIPD sample. | Governance docs and treatment inventory. |
| R5 | Overexposure from broad published schema | Medium | High | High | Keep published layer minimized to executive use cases. | Published contract and schema checks. |

## Controles Implementados

- Classificação de colunas com heurística + contrato YAML.
- Score de risco explicável com recomendação de publicação.
- Checks de qualidade integrados na decisão executiva.
- Camada publicada minimizada e pseudonimizada.

## Limitações

- Este RIPD é simulado para demonstração técnica.
- Não representa conformidade jurídica automática com LGPD.
- Requer validação com jurídico e segurança para dados pessoais reais.