# Privacidade, LGPD e Governança

Este documento registra as decisões de privacidade por design e governança aplicadas ao projeto.
Os controles aqui descritos são **LGPD-inspired privacy controls** para fins de engenharia e portfólio, sem representar parecer jurídico.

## Controles Alinhados à LGPD

O projeto usa o dataset público da Olist como caso analítico, mas aplica controles inspirados em privacidade por design para reduzir exposição desnecessária na camada publicada.
- `necessidade`: A camada publicada mantém apenas os atributos necessários para leitura executiva e remove identificadores transacionais e quase-identificadores.
- `adequacao`: O uso publicado é restrito a indicadores executivos, sem expor granularidade operacional desnecessária para esse propósito.
- `seguranca`: Chaves publicadas são pseudonimizadas antes do consumo e a camada interna permanece separada da camada exposta.
- `prevencao`: O pipeline falha quando detecta colunas proibidas, pseudonimização ausente ou vazamento de campos classificados como não publicáveis.

## Data classification e privacy risk scoring

- A classificação de colunas é materializada por `src/lgpd_classifier.py` com categorias como `non_personal`, `personal_data`, `sensitive_personal_data` e `indirect_identifier`.
- O risco é quantificado por `src/risk_scoring.py`, produzindo score explicável e nível de risco (`low`, `medium`, `high`).
- A decisão operacional deve considerar risco de privacidade, qualidade e contexto de uso do dado publicado.

## Camadas de Exposição

- `data/raw/landing/`: dados brutos recebidos sem transformação.
- `data/standardized/`: dados padronizados para reuso técnico.
- `data/curated/analytics/`: tabela analítica interna com granularidade por item, usada para processamento, SQL e qualidade.
- `data/published/dashboard/`: camada publicada e minimizada para consumo do Streamlit.

## Medidas Aplicadas na Camada Publicada

- pseudonimização não reversível de `order_id` e `customer_unique_id` antes do consumo pelo dashboard.
- pseudonimização não reversível de `seller_id` em `seller_key` para permitir recortes por seller sem expor o identificador bruto.
- remoção de identificadores desnecessários para apresentação, como `customer_id`, `seller_id` e `product_id`.
- remoção de quase-identificadores mais sensíveis na camada publicada, como cidade e prefixo de CEP.
- manutenção apenas de atributos necessários para responder às perguntas do projeto: tempo, categoria, UF, pagamento, valor, atraso, seller, logística e cohort.
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
- Colunas publicadas: **34**
- Resultado da validação LGPD/governança: **PASS**
- Evidência tabular dos checks: `data/curated/quality/privacy_governance_results.csv`

## Validação Aplicada

| Check | Status | Detalhes |
| --- | --- | --- |
| `required_columns` | **PASS** | Ausentes: nenhuma |
| `forbidden_columns_absent` | **PASS** | Presentes indevidas: nenhuma |
| `unexpected_columns` | **PASS** | Inesperadas: nenhuma |
| `pseudonymized__order_id` | **PASS** | Prefixo esperado: `order_id_` |
| `pseudonymized__customer_unique_id` | **PASS** | Prefixo esperado: `customer_unique_id_` |
| `pseudonymized__seller_key` | **PASS** | Prefixo esperado: `seller_id_` |
| `default_fill__customer_state` | **PASS** | nulls=0 | default_observado=False |
| `default_fill__seller_state` | **PASS** | nulls=0 | default_observado=False |
| `default_fill__order_status` | **PASS** | nulls=0 | default_observado=False |
| `default_fill__payment_type_mode` | **PASS** | nulls=0 | default_observado=True |
| `default_fill__seller_volume_tier` | **PASS** | nulls=0 | default_observado=True |
| `classification_leakage` | **PASS** | Colunas sensíveis expostas: nenhuma |

## Política de Uso

- o dashboard deve consumir exclusivamente a camada `published/dashboard`.
- a camada `curated/analytics` permanece interna ao pipeline e não deve ser tratada como camada de exposição.
- tabelas detalhadas do app devem exibir apenas chaves pseudonimizadas e dimensões agregadas necessárias ao projeto.
- uploads manuais em plataforma devem usar preferencialmente o CSV da camada publicada.

## Access considerations

- Este repositório demonstra controles técnicos de exposição, não um modelo corporativo completo de IAM.
- Em cenário real, recomenda-se matriz de acesso por persona (engenharia, analytics, negócio, auditoria).
- A camada interna (`curated`) deve permanecer restrita a papéis técnicos autorizados.
- Referência de portfólio para acesso e retenção: `docs/access_and_retention_policy.md`.

## Data minimization e publication controls

- A publicação aplica minimização ativa: somente colunas necessárias para consumo executivo.
- Identificadores são pseudonimizados para reduzir risco de reidentificação na camada de exposição.
- A publicação é bloqueada quando controles de governança não são atendidos.

## Masking/anonymization preview

- O projeto inclui preview técnico de transformações de privacidade no app executivo, com foco em entendimento de impacto de mascaramento/anonimização.
- As transformações são implementadas em `src/privacy_transformations.py` e exibidas em contexto analítico para suporte à decisão de publicação.
- O objetivo é demonstrar trade-off entre utilidade analítica e redução de exposição.

## Limitações e Escopo

- o dataset Olist é público e anonimizado, mas o projeto adota privacidade por design para refletir prática corporativa.
- esta camada não substitui controles organizacionais de acesso, mas reduz exposição desnecessária no produto analítico publicado.
- o projeto **não afirma conformidade jurídica plena com LGPD**; ele simula controles técnicos inspirados em boas práticas.

## Recommended production considerations

- definir matriz formal de acesso por persona e ambiente (dev/stage/prod);
- estabelecer política de retenção aprovada por jurídico/compliance;
- integrar auditoria de acessos e trilha de publicação em repositório central de logs;
- revisar periodicamente regras de classificação e pesos de risco conforme contexto de negócio;
- validar controles com áreas jurídica e de segurança antes de qualquer uso com dados pessoais reais.

