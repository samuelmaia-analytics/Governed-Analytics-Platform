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

| Metric | Definition | Formula | Granularity | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| Total Orders | Número total de pedidos únicos no período filtrado | `COUNT(DISTINCT order_id)` | período, estado, categoria, seller | `fact_orders_dashboard` | `order_id` é pseudonimizado na camada publicada |
| GMV | Valor bruto de mercadoria no período | `SUM(revenue)` | período, estado, categoria, seller | `fact_orders_dashboard` | não representa margem líquida |
| Average Ticket | Receita média por pedido | `SUM(revenue) / COUNT(DISTINCT order_id)` | período, estado, categoria, seller | `fact_orders_dashboard` | sensível a outliers de receita |
| Delivery Delay | Atraso médio de entrega em dias | `AVG(delivery_delay_days)` | período, estado, categoria, seller | `fact_orders_dashboard` / `logistics_slice` | considerar distribuição e não apenas média |
| Data Quality Score | Índice agregado de qualidade do dataset | regra agregada dos checks (`PASS/FAIL`) com pesos por severidade | execução de pipeline | saídas de `src/data_quality.py` e `src/data_quality_rules.py` | usar junto com tabela detalhada de checks |
| Privacy Risk Score | Score explicável de risco de privacidade | composição ponderada dos sinais de classificação LGPD e exposição | execução de pipeline | `src/lgpd_classifier.py` + `src/risk_scoring.py` | interpretação: low / medium / high |
| Publication Readiness | Prontidão para publicação da camada publicada | estado derivado de qualidade + risco + controles de publicação | execução de pipeline | `src/publish_dashboard.py` + `src/governance_control_center` | estados esperados: `Approved`, `Needs Review`, `Blocked` |

## Convenções recomendadas

- Sempre apresentar KPI com janela temporal explícita.
- Evitar comparar métricas de grãos diferentes sem normalização.
- Exibir, quando possível, `valor atual`, `variação` e `contexto` (filtro aplicado).

## Limitações conhecidas

- O projeto usa dados públicos e sintéticos para demonstração de governança e analytics engineering.
- Métricas executivas são orientadas a portfólio e podem exigir ajuste para cenários de negócio específicos.

