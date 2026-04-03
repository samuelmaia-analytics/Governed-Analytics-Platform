# Dicionário de Dados

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/olist-governed-analytics-platform`
- Dashboard Streamlit: `https://olist-governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

## Visão Geral

Este documento consolida o dicionário de dados do projeto `olist_governed_analytics_platform`, descrevendo os principais ativos raw e processed, com foco especial na tabela analítica `fact_orders_enriched`, na camada publicada `fact_orders_dashboard` e nos novos ativos semânticos e operacionais. A fonte pública utilizada é o `Brazilian E-Commerce Public Dataset by Olist`, disponibilizado no Kaggle em `https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce`.

O objetivo deste material é documentar:

- origem e finalidade dos ativos de dados
- granularidade de cada dataset
- significado das colunas mais relevantes
- regras de negócio aplicadas
- observações de qualidade para uso analítico

## 1. Ativos Raw

Os ativos raw correspondem aos arquivos originais do dataset Olist, armazenados em `data/raw/landing/olist/`.

| Ativo | Caminho | Descrição | Granularidade |
| --- | --- | --- | --- |
| `olist_orders_dataset.csv` | `data/raw/landing/olist/olist_orders_dataset.csv` | Base principal de pedidos com status e datas do ciclo do pedido. | 1 linha por pedido |
| `olist_order_items_dataset.csv` | `data/raw/landing/olist/olist_order_items_dataset.csv` | Itens vendidos em cada pedido, com seller, produto, preço e frete. | 1 linha por item de pedido |
| `olist_products_dataset.csv` | `data/raw/landing/olist/olist_products_dataset.csv` | Cadastro de produtos e atributos físicos. | 1 linha por produto |
| `olist_customers_dataset.csv` | `data/raw/landing/olist/olist_customers_dataset.csv` | Identificação e localidade dos clientes. | 1 linha por cliente transacional |
| `olist_sellers_dataset.csv` | `data/raw/landing/olist/olist_sellers_dataset.csv` | Cadastro de sellers com localidade. | 1 linha por seller |
| `olist_order_payments_dataset.csv` | `data/raw/landing/olist/olist_order_payments_dataset.csv` | Informações de pagamentos dos pedidos. | 1 linha por evento de pagamento |
| `olist_order_reviews_dataset.csv` | `data/raw/landing/olist/olist_order_reviews_dataset.csv` | Avaliações dos pedidos e timestamps associados. | 1 linha por review |
| `olist_geolocation_dataset.csv` | `data/raw/landing/olist/olist_geolocation_dataset.csv` | Base geográfica por CEP prefixado. | 1 linha por observação geográfica |
| `product_category_name_translation.csv` | `data/raw/landing/olist/product_category_name_translation.csv` | Tradução de categoria de produto para inglês. | 1 linha por categoria |

## 2. Ativos Processed

Os ativos processed representam as saídas geradas pelo pipeline analítico do projeto.

| Ativo | Caminho | Descrição | Granularidade |
| --- | --- | --- | --- |
| `olist/*.parquet` | `data/standardized/olist/` | Tabelas padronizadas promovidas a partir da landing. | 1 linha por registro de origem |
| `profiling/*.csv` | `data/staging/profiling/` | Perfis exploratórios, nulos, chaves candidatas e duplicidade. | Variável por artefato |
| `fact_orders_enriched.parquet` | `data/curated/analytics/fact_orders_enriched.parquet` | Tabela analítica principal do projeto. | 1 linha por item de pedido |
| `fact_orders_enriched.csv` | `data/curated/analytics/fact_orders_enriched.csv` | Versão CSV da tabela analítica principal. | 1 linha por item de pedido |
| `fact_orders_dashboard.parquet` | `data/published/dashboard/fact_orders_dashboard.parquet` | Camada publicada minimizada para o dashboard e publicação externa. | 1 linha por item de pedido |
| `fact_orders_dashboard.csv` | `data/published/dashboard/fact_orders_dashboard.csv` | Versão tabular da camada publicada para upload manual na plataforma. | 1 linha por item de pedido |
| `logistics_slice.parquet` | `data/published/semantic/logistics_slice.parquet` | Mart agregado para leitura logística por período e UF origem/destino. | 1 linha por combinação agregada |
| `seller_slice.parquet` | `data/published/semantic/seller_slice.parquet` | Mart agregado para desempenho por seller pseudonimizado. | 1 linha por seller |
| `cohort_slice.parquet` | `data/published/semantic/cohort_slice.parquet` | Mart agregado para cohort e maturação de compra. | 1 linha por cohort e mês relativo |
| `category_slice.parquet` | `data/published/semantic/category_slice.parquet` | Mart agregado para receita, atraso, review e pagamento por categoria e mês. | 1 linha por categoria, mês e meio de pagamento |
| `state_performance_slice.parquet` | `data/published/semantic/state_performance_slice.parquet` | Mart agregado para leitura executiva de receita, sellers ativos, atraso e satisfação por UF e mês. | 1 linha por UF e mês |
| `published_layer_monitoring.csv` | `data/published/monitoring/published_layer_monitoring.csv` | Resultado estruturado do monitoramento recorrente da camada publicada. | 1 linha por check |
| `published_layer_monitoring.json` | `data/published/monitoring/published_layer_monitoring.json` | Resumo serializado da execução de monitoramento. | 1 documento por execução |
| `operational_job_results.json` | `data/curated/ops/operational_job_results.json` | Resultado do runner operacional por etapa. | 1 documento por execução |
| `fact_orders_enriched_quality_checks.csv` | `data/curated/quality/fact_orders_enriched_quality_checks.csv` | Resultado estruturado dos checks de qualidade da tabela analítica. | 1 linha por check |
| `query_results/*.csv` | `data/curated/query_results/` | Resultados das queries analíticas executadas em DuckDB. | Variável por consulta |
| `dadosfera_collection.json` | `data/curated/catalog/dadosfera_collection.json` | Manifesto versionável da coleção do projeto. | 1 documento por coleção |
| `collection_assets_inventory.csv` | `data/curated/catalog/collection_assets_inventory.csv` | Inventário tabular dos ativos do projeto. | 1 linha por ativo |
| `bi_exports/*.csv` | `data/processed/bi_exports/` | Exportações auxiliares para consumo em Power BI. | Variável por dataset |

## 3. Tabela Analítica Final

### `fact_orders_enriched`

**Caminho**

- `data/curated/analytics/fact_orders_enriched.parquet`
- `data/curated/analytics/fact_orders_enriched.csv`

**Descrição**

Tabela analítica consolidada para análise de pedidos, itens, receita, logística, seller, cohort, experiência do cliente e distribuição geográfica.

**Granularidade**

`1 linha por item de pedido`, definida pela combinação:

- `order_id`
- `order_item_id`
- `product_id`
- `seller_id`

**Regras de negócio principais**

- `order_items` é a base factual principal
- `orders`, `customers`, `products`, `sellers` e `translation` entram por joins dimensionais
- `payments` e `reviews` são agregados por `order_id` antes do join
- `total_item_value` = `price + freight_value`
- `delivery_time_days` mede o tempo entre compra e entrega
- `seller_dispatch_time_days` mede o tempo entre aprovação e despacho para a transportadora
- `carrier_delivery_time_days` mede o trecho transportadora -> cliente
- `purchase_cohort_month`, `customer_order_sequence` e `cohort_order_month_number` suportam análise de cohort
- `seller_order_count`, `seller_delay_rate` e `seller_volume_tier` suportam recortes de seller

## 3.1 Classificação de Sensibilidade

| Classe | Descrição | Exemplos no projeto |
| --- | --- | --- |
| `Analítico público` | Pode ser exposto em dashboard, markdown e prints sem granularidade sensível adicional. | métricas agregadas por categoria, tempo, UF, pagamento |
| `Analítico interno` | Necessário para engenharia, SQL e qualidade, mas não para exposição direta em app executivo. | `fact_orders_enriched` |
| `Quase-identificador` | Não identifica diretamente, mas pode aumentar risco por combinação. | `customer_city`, `seller_city`, `customer_zip_code_prefix`, `seller_zip_code_prefix`, timestamps detalhados |
| `Identificador pseudonimizado` | Chave mantida apenas para contagem, deduplicação e drill-down controlado. | `order_id`, `customer_unique_id` e `seller_key` na camada publicada |

## 4. Colunas-Chave da `fact_orders_enriched`

| Coluna | Tipo | Descrição | Regra de negócio |
| --- | --- | --- | --- |
| `order_id` | `string` | Identificador do pedido. | Chave de pedido oriunda de `orders`. |
| `order_item_id` | `integer` | Sequencial do item dentro do pedido. | Parte da granularidade final. |
| `customer_unique_id` | `string` | Identificador único consolidado do cliente. | Permite análise de recorrência. |
| `seller_id` | `string` | Identificador do seller. | Join com dimensão de sellers. |
| `order_purchase_timestamp` | `datetime` | Timestamp de compra do pedido. | Marco inicial do ciclo do pedido. |
| `order_approved_at` | `datetime` | Timestamp de aprovação do pedido. | Referência para coerência temporal. |
| `order_delivered_carrier_date` | `datetime` | Data de entrega ao transportador. | Marco intermediário do fluxo logístico. |
| `order_delivered_customer_date` | `datetime` | Data de entrega ao cliente. | Marco final da entrega. |
| `order_estimated_delivery_date` | `datetime` | Data estimada de entrega. | Base para cálculo de atraso. |
| `purchase_cohort_month` | `string` | Cohort mensal da primeira compra do cliente. | Derivada do primeiro timestamp de compra. |
| `cohort_order_month_number` | `integer` | Distância em meses desde a primeira compra. | Usada em leitura de maturação de cohort. |
| `customer_order_sequence` | `integer` | Ordem da compra do cliente. | Rank denso por cliente. |
| `is_first_order` | `boolean` | Indicador de primeira compra. | `True` quando `customer_order_sequence = 1`. |
| `delivery_time_days` | `float` | Tempo entre compra e entrega. | `order_delivered_customer_date - order_purchase_timestamp`. |
| `seller_dispatch_time_days` | `float` | Tempo entre aprovação e despacho. | `order_delivered_carrier_date - order_approved_at`. |
| `carrier_delivery_time_days` | `float` | Tempo entre despacho e entrega final. | `order_delivered_customer_date - order_delivered_carrier_date`. |
| `estimated_delay_days` | `float` | Diferença entre entrega real e estimada. | `order_delivered_customer_date - order_estimated_delivery_date`. |
| `is_delayed` | `boolean` | Indicador de atraso na entrega. | `True` quando entrega real > estimada. |
| `price` | `float` | Valor do item. | Oriundo de `order_items`. |
| `freight_value` | `float` | Valor do frete. | Oriundo de `order_items`. |
| `freight_to_price_ratio` | `float` | Peso relativo do frete sobre o item. | `freight_value / price` quando `price > 0`. |
| `total_item_value` | `float` | Valor total do item com frete. | `price + freight_value`. |
| `seller_order_count` | `integer` | Total de pedidos por seller. | Derivado por agrupamento do seller. |
| `seller_avg_delivery_days` | `float` | Tempo médio de entrega do seller. | Média de `delivery_time_days` por seller. |
| `seller_delay_rate` | `float` | Taxa média de atraso do seller. | Média de `is_delayed` por seller. |
| `seller_volume_tier` | `string` | Faixa de volume operacional do seller. | Classificação por volume de pedidos. |
| `payment_type_mode` | `string` | Meio de pagamento dominante do pedido. | Moda de `payment_type` por pedido. |
| `review_score_mean` | `float` | Nota média de review do pedido. | Média de `review_score` por `order_id`. |
| `product_category_name` | `string` | Categoria do produto em português. | Oriunda da tabela de produtos. |
| `customer_state` | `string` | UF do cliente. | Principal dimensão geográfica do projeto. |
| `seller_state` | `string` | UF do seller. | Dimensão de origem logística e supply. |

## 5. Camada Publicada para Dashboard

### `fact_orders_dashboard`

**Caminho**

- `data/published/dashboard/fact_orders_dashboard.parquet`
- `data/published/dashboard/fact_orders_dashboard.csv`

**Objetivo**

Camada publicada para o Streamlit e para publicação externa, derivada de `fact_orders_enriched` com minimização e pseudonimização.

**Principais decisões**

- `order_id` e `customer_unique_id` permanecem apenas em formato pseudonimizado
- `seller_id` é transformado em `seller_key`
- `customer_id`, `product_id`, `seller_id`, cidade e prefixo de CEP não são publicados
- a camada mantém apenas colunas necessárias para perguntas executivas, semântica de seller, logística e cohort

## 6. Camada Semântica Publicada

Os marts publicados ampliam consumo sem expor a granularidade inteira da camada publicada.

| Ativo | Objetivo | Principais métricas |
| --- | --- | --- |
| `logistics_slice` | leitura logística agregada | atraso, tempo médio de entrega, despacho, transporte, peso relativo do frete |
| `seller_slice` | leitura de desempenho por seller pseudonimizado | ticket médio, atraso, tempo médio, review, tier de volume |
| `cohort_slice` | leitura de retenção e maturação | clientes, pedidos, itens, ticket médio, atraso |
| `category_slice` | leitura de categoria e monetização | receita, ticket, review, atraso, meio de pagamento |
| `state_performance_slice` | leitura executiva por UF | receita, sellers ativos, atraso, satisfação, tempo médio |

## 7. Monitoramento da Camada Publicada

O monitoramento recorrente da `published` registra:

- freshness do arquivo publicado
- schema esperado
- duplicidade de chave publicada
- volume mínimo
- nulos críticos
- cobertura semântica de cohort e seller
- disparo opcional de alertas externos via webhook quando há falhas

Ativos relevantes:

- `data/published/monitoring/published_layer_monitoring.csv`
- `data/published/monitoring/published_layer_monitoring.json`
- `docs/published_layer_monitoring.md`

## 8. Observações Gerais de Qualidade

- a base final possui mais de `100.000` registros e atende ao volume mínimo esperado do projeto
- a granularidade escolhida não apresentou duplicidade na validação atual
- há uma anomalia residual da fonte em poucos registros de coerência temporal, tratada como alerta e não mascarada
- a camada publicada e os marts semânticos passam por materialização controlada antes do consumo

## 9. Uso Recomendado

Use preferencialmente:

- `fact_orders_enriched` para engenharia, SQL, qualidade e auditoria
- `fact_orders_dashboard` para consumo executivo e publicação externa
- `logistics_slice`, `seller_slice`, `cohort_slice`, `category_slice` e `state_performance_slice` para recortes agregados adicionais
- `published_layer_monitoring` para observabilidade operacional da camada publicada

