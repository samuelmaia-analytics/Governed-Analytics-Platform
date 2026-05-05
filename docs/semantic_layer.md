# Camada Semântica e Métricas

Este documento descreve a camada semântica publicada e o dicionário de métricas usado no app executivo e nos artefatos analíticos.

## Objetivo

- padronizar definições de KPI para evitar ambiguidade entre app, SQL e exportações;
- explicitar granularidade e fonte de cada métrica;
- reforçar a separação entre camada analítica interna e camada publicada para consumo.

## Fronteira de dados

- Camada interna (engenharia): `data/curated/analytics/`
- Camada publicada (consumo): `data/published/dashboard/` e `data/published/semantic/`
- O dashboard executivo deve consumir apenas a camada publicada.

## Marts publicados

- `logistics_slice`
- `seller_slice`
- `cohort_slice`
- `category_slice`
- `state_performance_slice`

Esses marts são derivados da camada publicada para suportar leitura executiva e recortes operacionais sem expor a camada interna completa.

## Dicionário de métricas

| metric_name | business_definition | formula | grain | source_layer | business_owner | notes |
| --- | --- | --- | --- | --- | --- | --- |
| Total Orders | Total de pedidos únicos no período analisado | `COUNT(DISTINCT order_id)` | período, estado, categoria, seller | `published/dashboard` | Analytics | `order_id` é pseudonimizado na camada publicada |
| GMV | Valor bruto de mercadoria no período | `SUM(revenue)` | período, estado, categoria, seller | `published/dashboard` | Business + Analytics | não representa margem líquida |
| Average Ticket | Receita média por pedido | `SUM(revenue) / COUNT(DISTINCT order_id)` | período, estado, categoria, seller | `published/dashboard` | Analytics | sensível a outliers de receita |
| Delivery Delay | Atraso médio de entrega em dias | `AVG(delivery_delay_days)` | período, estado, categoria, seller | `published/dashboard`, `published/semantic/logistics_slice` | Operations + Analytics | usar mediana/percentis junto da média |
| Data Quality Score | Indicador agregado de qualidade da execução | agregação dos checks de qualidade por severidade | execução de pipeline | `curated/quality` e artefatos de qualidade publicados | Data Governance | deve ser lido com detalhe de checks |
| Privacy Risk Score | Score explicável de risco de privacidade | composição ponderada de sinais LGPD e exposição | execução de pipeline | saídas de `src/lgpd_classifier.py` e `src/risk_scoring.py` | Data Governance | interpretação: `low`, `medium`, `high` |
| Publication Readiness | Estado de prontidão para publicação executiva | decisão derivada de qualidade + risco + controles de publicação | execução de pipeline | `published/dashboard` + artefatos de governança | Data Governance + Analytics | estados esperados: `Approved`, `Needs Review`, `Blocked` |

## Convenções recomendadas

- Sempre apresentar KPI com janela temporal explícita.
- Evitar comparar métricas de grãos diferentes sem normalização.
- Exibir, quando possível, `valor atual`, `variação` e `contexto` (filtro aplicado).

## Riscos de ambiguidade de métricas

- **GMV vs Revenue líquida**: este projeto usa receita bruta (`revenue`) para leitura executiva; margem e devoluções não estão modeladas como KPI financeiro final.
- **Average Ticket**: precisa de definição consistente do denominador (`order_id` único) para evitar distorção por granularidade de item.
- **Delivery Delay**: média isolada pode mascarar caudas; recomenda-se acompanhar percentis.
- **Publication Readiness**: é um estado operacional de governança, não um KPI de negócio.

## Como a camada semântica ajuda o consumo executivo

- reduz variação de definição entre app, SQL e exportação BI;
- centraliza fórmulas e grãos para evitar divergência em reuniões executivas;
- acelera leitura de status de publicação, qualidade e risco sem depender da camada interna completa.

## Limitações conhecidas

- O projeto usa dados públicos e sintéticos para demonstração de governança e analytics engineering.
- Métricas executivas são orientadas a portfólio e podem exigir ajuste para cenários de negócio específicos.

