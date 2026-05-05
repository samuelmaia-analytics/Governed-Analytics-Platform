# Mini RIPD Sample (LGPD-inspired)

> Documento técnico simulado para portfólio.
> Não substitui avaliação jurídica formal.

## Escopo

- Produto: Governed Analytics Platform
- Dataset publicado: `fact_orders_dashboard`
- Contexto: consumo executivo interno

## Resumo da operação

- classificação de colunas por sensibilidade;
- score de risco explicável;
- validação de qualidade antes da publicação;
- minimização e pseudonimização na camada publicada.

## Inventário de tratamento (simulado)

| Campo | Valor |
| --- | --- |
| Finalidade | Executive performance and governance monitoring |
| Base legal | legitimate_interest (simulated) |
| Controlador | Olist Governed Analytics (fictitious) |
| Operador | Analytics Platform Team (fictitious) |
| Encarregado | dpo@example.org (fictitious) |
| Retenção | 12 meses (published), 24 meses (curated) - simulated |

## Matriz resumida de risco

| Risco | Probabilidade | Impacto | Severidade | Mitigação |
| --- | --- | --- | --- | --- |
| Vazamento de identificadores | Média/Alta | Alta | Alta/Crítica | remoção/pseudonimização |
| Reidentificação por quase-identificadores | Média | Média | Média/Alta | minimização e agregação |
| Publicação com falhas de qualidade | Média | Média | Média/Alta | bloqueio/revisão por checks |

## Controles implementados

- contrato de governança de publicação;
- validação de colunas proibidas e obrigatórias;
- pseudonimização de chaves sensíveis;
- decisão de publicação baseada em risco + qualidade.

## Limitações

- amostra orientada a portfólio;
- controles jurídicos e organizacionais não estão completos;
- não representa certificação de conformidade LGPD.
