# Camada Semântica

Este documento define a camada semântica usada para consumo executivo.
O objetivo é reduzir ambiguidades de KPI entre pipeline, app e exportações.

## Objetivo

- padronizar definições de métricas;
- explicitar fórmulas e granularidade;
- alinhar fonte de dados por métrica;
- manter linguagem única para analytics e negócio.

## Escopo

Esta camada serve ao consumo publicado.
Ela não substitui a camada analítica interna detalhada.

## Fronteira de dados

- camada interna: `data/curated/analytics/`
- camada publicada: `data/published/dashboard/`
- recortes semânticos: `data/published/semantic/`

## Métricas principais

| metric_name | business_definition | formula | grain | source_layer | business_owner | notes |
| --- | --- | --- | --- | --- | --- | --- |
| Total Orders | Total de pedidos únicos no período analisado | `COUNT(DISTINCT order_id)` | período, estado, categoria, seller | `published/dashboard` | Analytics | `order_id` é pseudonimizado na camada publicada |
| GMV | Valor bruto de mercadoria no período | `SUM(revenue)` | período, estado, categoria, seller | `published/dashboard` | Business + Analytics | não representa margem líquida |
| Average Ticket | Receita média por pedido | `SUM(revenue) / COUNT(DISTINCT order_id)` | período, estado, categoria, seller | `published/dashboard` | Analytics | sensível a outliers |
| Delivery Delay | Atraso médio de entrega em dias | `AVG(delivery_delay_days)` | período, estado, categoria, seller | `published/dashboard`, `published/semantic/logistics_slice` | Operations + Analytics | acompanhar mediana e percentis |
| Data Quality Score | Indicador agregado de qualidade da execução | agregação dos checks por severidade | execução do pipeline | `curated/quality` e saídas publicadas | Data Governance | interpretar junto com tabela detalhada |
| Privacy Risk Score | Score explicável de risco de privacidade | composição ponderada de sinais LGPD e exposição | execução do pipeline | `src/lgpd_classifier.py`, `src/risk_scoring.py` | Data Governance | níveis: `low`, `medium`, `high` |
| Publication Readiness | Estado de prontidão para publicação | regra derivada de qualidade + risco + controles | execução do pipeline | `published/dashboard` e artefatos de governança | Data Governance + Analytics | estados: `Approved`, `Needs Review`, `Blocked` |

## Convenções de consumo

- sempre informar janela temporal aplicada;
- evitar comparação direta de métricas com grãos diferentes;
- manter mesma definição em app, relatório e exportação;
- exibir contexto do filtro no valor apresentado.

## Riscos de ambiguidade

### GMV

GMV é receita bruta de mercadoria.
Não deve ser comunicado como lucro.

### Average Ticket

Depende de denominador consistente de pedido único.
Mudança de grão pode distorcer leitura.

### Delivery Delay

Média isolada pode mascarar caudas.
É recomendado incluir percentis para operação.

### Publication Readiness

É status operacional de governança.
Não é KPI de performance comercial.

## Uso executivo

A camada semântica facilita leitura executiva ao:

- centralizar definições de KPI;
- manter rastreabilidade mínima para auditoria;
- reduzir divergência entre narrativas de diferentes áreas.

## Limitações

- projeto orientado a portfólio com dados públicos/sintéticos;
- fórmulas podem exigir ajuste para regras financeiras reais;
- a camada publicada prioriza decisão executiva, não exploração analítica profunda.
