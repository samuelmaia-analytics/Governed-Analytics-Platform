# Privacidade, LGPD e Governança


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento registra as decisões de privacidade por design e governança aplicadas ao case.

## Camadas de Exposição

- `data/raw/landing/`: dados brutos recebidos sem transformação.
- `data/standardized/`: dados padronizados para reuso técnico.
- `data/curated/analytics/`: tabela analítica interna com granularidade por item, usada para processamento, SQL e qualidade.
- `data/published/dashboard/`: camada publicada e minimizada para consumo do Streamlit.

## Medidas Aplicadas na Camada Publicada

- pseudonimização não reversível de `order_id` e `customer_unique_id` antes do consumo pelo dashboard.
- remoção de identificadores desnecessários para apresentação, como `customer_id`, `seller_id` e `product_id`.
- remoção de quase-identificadores mais sensíveis na camada publicada, como cidade e prefixo de CEP.
- manutenção apenas de atributos necessários para responder às perguntas do case: tempo, categoria, UF, pagamento, valor, atraso e satisfação.
- preservação da camada analítica interna para engenharia e auditoria, separada da camada publicada.

## Colunas Removidas da Camada Publicada

| Coluna removida | Motivo principal |
| --- | --- |
| `customer_id` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `product_id` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `seller_id` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `customer_zip_code_prefix` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `customer_city` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `seller_zip_code_prefix` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `seller_city` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `latest_review_creation_date` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `latest_review_answer_timestamp` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `shipping_limit_date` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `order_delivered_carrier_date` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `order_approved_at` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `payment_count` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `total_payment_value` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `max_payment_installments` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `review_count` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `review_score_max` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `review_score_min` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |
| `has_review_comment` | Minimização e redução de risco de reidentificação sem perda do objetivo analítico do dashboard. |

## Resultado da Publicação Segura

- Arquivo publicado para o app: `data/published/dashboard/fact_orders_dashboard.parquet`
- Arquivo publicado para upload manual: `data/published/dashboard/fact_orders_dashboard.csv`
- Registros publicados: **112,650**
- Colunas publicadas: **22**

## Política de Uso

- o dashboard deve consumir exclusivamente a camada `published/dashboard`.
- a camada `curated/analytics` permanece interna ao pipeline e não deve ser tratada como camada de exposição.
- tabelas detalhadas do app devem exibir apenas chaves pseudonimizadas e dimensões agregadas necessárias ao case.
- uploads manuais em plataforma devem usar preferencialmente o CSV da camada publicada.

## Limitações e Escopo

- o dataset Olist é público e anonimizado, mas o projeto adota privacidade por design para refletir prática corporativa.
- esta camada não substitui controles organizacionais de acesso, mas reduz exposição desnecessária no produto analítico publicado.



