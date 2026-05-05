# Classificação de Dados

Este documento materializa a classificação dos principais campos com impacto de privacidade e governança no projeto.

## Critérios

- `identificador_indireto`: chave transacional ou persistente que não identifica diretamente, mas permite rastreamento.
- `quase_identificador`: atributo que, em combinação com outros, aumenta risco de reidentificação.
- `identificador_pseudonimizado`: chave transformada para preservar uso analítico com menor exposição.
- `analitico_publico` ou `analitico_agregado`: atributo adequado à camada publicada por ser necessário e de baixo risco.

## Inventário

| Asset | Coluna | Camada | Classificação | Risco | Ação na publicada | Publicável |
| --- | --- | --- | --- | --- | --- | --- |
| `fact_orders_enriched` | `order_id` | `curated_internal` | `identificador_indireto` | `medium` | `pseudonymize` | `False` |
| `fact_orders_enriched` | `customer_id` | `curated_internal` | `dado_pessoal_indireto` | `high` | `remove` | `False` |
| `fact_orders_enriched` | `customer_unique_id` | `curated_internal` | `dado_pessoal_indireto` | `high` | `pseudonymize` | `False` |
| `fact_orders_enriched` | `customer_city` | `curated_internal` | `quase_identificador` | `high` | `remove` | `False` |
| `fact_orders_enriched` | `customer_zip_code_prefix` | `curated_internal` | `quase_identificador` | `high` | `remove` | `False` |
| `fact_orders_enriched` | `seller_id` | `curated_internal` | `identificador_comercial` | `medium` | `remove` | `False` |
| `fact_orders_enriched` | `seller_city` | `curated_internal` | `quase_identificador` | `medium` | `remove` | `False` |
| `fact_orders_enriched` | `seller_zip_code_prefix` | `curated_internal` | `quase_identificador` | `medium` | `remove` | `False` |
| `fact_orders_enriched` | `review_comment_message` | `source_only` | `texto_livre_potencialmente_sensivel` | `high` | `aggregate_or_remove` | `False` |
| `fact_orders_dashboard` | `order_id` | `published_dashboard` | `identificador_pseudonimizado` | `low_medium` | `keep` | `True` |
| `fact_orders_dashboard` | `customer_unique_id` | `published_dashboard` | `identificador_pseudonimizado` | `low_medium` | `keep` | `True` |
| `fact_orders_dashboard` | `seller_key` | `published_dashboard` | `identificador_pseudonimizado` | `low_medium` | `keep` | `True` |
| `fact_orders_dashboard` | `customer_state` | `published_dashboard` | `analitico_agregado` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `seller_state` | `published_dashboard` | `analitico_agregado` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `purchase_cohort_month` | `published_dashboard` | `analitico_agregado` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `customer_order_sequence` | `published_dashboard` | `analitico_publico` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `seller_volume_tier` | `published_dashboard` | `analitico_agregado` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `seller_delay_rate` | `published_dashboard` | `analitico_publico` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `total_item_value` | `published_dashboard` | `analitico_publico` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `delivery_time_days` | `published_dashboard` | `analitico_publico` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `seller_dispatch_time_days` | `published_dashboard` | `analitico_publico` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `carrier_delivery_time_days` | `published_dashboard` | `analitico_publico` | `low` | `keep` | `True` |
| `fact_orders_dashboard` | `freight_to_price_ratio` | `published_dashboard` | `analitico_publico` | `low` | `keep` | `True` |
