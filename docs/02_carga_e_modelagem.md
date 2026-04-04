# 02 Carga e Modelagem

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/governed-analytics-platform`
- Dashboard Streamlit: `https://governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento resume como os dados entram no projeto, como a modelagem foi estruturada e como a camada analítica interna é convertida em uma camada publicada segura e reutilizável.

## Tese de Carga e Modelagem

O projeto foi desenhado para separar claramente:

- ingestão e padronização
- modelagem analítica interna
- publicação segura para consumo
- expansão semântica e observabilidade operacional

Isso evita usar a tabela analítica completa como fonte direta de apresentação e reduz o acoplamento entre engenharia e consumo.

## Camadas Implementadas

- `data/raw/landing/olist/`
- `data/standardized/olist/`
- `data/staging/profiling/`
- `data/curated/analytics/`
- `data/curated/quality/`
- `data/curated/ops/`
- `data/published/dashboard/`
- `data/published/semantic/`
- `data/published/monitoring/`

## Scripts Principais

- `src/ingest.py`
- `src/preprocess.py`
- `src/build_analytics.py`
- `src/publish_dashboard.py`
- `src/semantic_layer.py`
- `src/published_monitoring.py`

## Modelagem Principal

### Ativo central

- `fact_orders_enriched`

### Granularidade

- `1 linha por item de pedido`

### Volume confirmado

- `112.650` registros

### Base factual escolhida

- `order_items`

Essa decisão preserva o nível em que preço, frete, seller, produto e entrega fazem sentido analítico sem perder contexto de pedido, pagamento, review e cliente.

## O Que a Modelagem Passou a Cobrir

Além do recorte original de receita, atraso, categoria e geografia, a modelagem agora já expõe semântica suficiente para:

- logística
- seller
- cohort e recorrência

Principais derivadas adicionadas:

- `purchase_cohort_month`
- `cohort_order_month_number`
- `customer_order_sequence`
- `is_first_order`
- `seller_dispatch_time_days`
- `carrier_delivery_time_days`
- `freight_to_price_ratio`
- `seller_order_count`
- `seller_avg_delivery_days`
- `seller_delay_rate`
- `seller_volume_tier`

## Camada Publicada para Consumo

O projeto separa explicitamente a camada analítica interna da camada publicada.

### Camada analítica interna

- ativo: `fact_orders_enriched`
- local: `data/curated/analytics/`
- uso: SQL, qualidade, governança, semântica e rastreabilidade

### Camada publicada

- ativo: `fact_orders_dashboard`
- local: `data/published/dashboard/`
- formatos:
  - `fact_orders_dashboard.parquet`
  - `fact_orders_dashboard.csv`

### Camadas derivadas publicadas

- `data/published/semantic/logistics_slice.parquet`
- `data/published/semantic/seller_slice.parquet`
- `data/published/semantic/cohort_slice.parquet`
- `data/published/monitoring/published_layer_monitoring.csv`

Uso recomendado:

- `parquet`: consumo local e camada oficial do Streamlit
- `csv`: upload manual e publicação tabular externa
- `semantic`: recortes agregados adicionais
- `monitoring`: observabilidade operacional da camada publicada

## Leitura Correta do Desenho

O projeto não usa a modelagem apenas para responder queries. Ele transforma a modelagem em produto analítico publicável.

Isso significa:

- a camada interna permanece rica e auditável
- a camada publicada é minimizada e governada
- os marts semânticos estendem consumo sem reabrir granularidade completa
- o monitoramento fecha o ciclo operacional da exposição

## Referências

- tabela analítica: [docs/fact_orders_enriched.md](./fact_orders_enriched.md)
- dicionário de dados: [docs/data_dictionary.md](./data_dictionary.md)
- qualidade: [docs/data_quality_report.md](./data_quality_report.md)
- publicação segura: [docs/privacy_governance.md](./privacy_governance.md)

