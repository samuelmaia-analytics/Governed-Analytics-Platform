# Dicionário de Dados

## Visão Geral

Este documento consolida o dicionário de dados do projeto `samuelmaia_DDF_032026`, descrevendo os principais ativos raw e processed, com foco especial na tabela analítica final `fact_orders_enriched`.

O objetivo deste material é documentar:

- origem e finalidade dos ativos de dados
- granularidade de cada dataset
- significado das colunas mais relevantes
- regras de negócio aplicadas
- observações de qualidade importantes para uso analítico

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
| `profiling_overview.csv` | `data/staging/profiling/profiling_overview.csv` | Resumo consolidado do profiling exploratório inicial. | 1 linha por tabela raw |
| `all_columns_profile.csv` | `data/staging/profiling/all_columns_profile.csv` | Perfil de colunas das tabelas raw. | 1 linha por coluna |
| `all_nulls_profile.csv` | `data/staging/profiling/all_nulls_profile.csv` | Nulos por coluna nas tabelas raw. | 1 linha por coluna |
| `all_possible_keys.csv` | `data/staging/profiling/all_possible_keys.csv` | Possíveis chaves candidatas identificadas por unicidade. | 1 linha por coluna candidata |
| `all_duplicate_profile.csv` | `data/staging/profiling/all_duplicate_profile.csv` | Duplicidade por tabela raw. | 1 linha por tabela |
| `fact_orders_enriched.parquet` | `data/curated/analytics/fact_orders_enriched.parquet` | Tabela analítica principal do projeto. | 1 linha por item de pedido |
| `fact_orders_enriched.csv` | `data/curated/analytics/fact_orders_enriched.csv` | Versão CSV da tabela analítica principal. | 1 linha por item de pedido |
| `fact_orders_dashboard.parquet` | `data/published/dashboard/fact_orders_dashboard.parquet` | Camada publicada para o dashboard, com pseudonimização e minimização. | 1 linha por item de pedido |
| `fact_orders_enriched_quality_checks.csv` | `data/curated/quality/fact_orders_enriched_quality_checks.csv` | Resultado estruturado dos checks de qualidade da tabela final. | 1 linha por check |
| `query_results/*.csv` | `data/curated/query_results/` | Resultados das queries analíticas executadas em DuckDB. | Variável por consulta |
| `dadosfera_collection.json` | `data/curated/catalog/dadosfera_collection.json` | Manifesto versionável da coleção do case com metadados de publicação e ativos catalogáveis. | 1 documento por coleção |
| `collection_assets_inventory.csv` | `data/curated/catalog/collection_assets_inventory.csv` | Inventário tabular dos ativos do projeto usados para catalogação/publicação. | 1 linha por ativo |
| `bi_exports/*.csv` | `data/processed/bi_exports/` | Exportações auxiliares para consumo em Power BI. | Variável por dataset |

## 3. Tabela Analítica Final

### `fact_orders_enriched`

**Caminho**

- `data/curated/analytics/fact_orders_enriched.parquet`
- `data/curated/analytics/fact_orders_enriched.csv`

**Descrição**

Tabela analítica consolidada para análise de pedidos, itens, receita, logística, experiência do cliente e distribuição geográfica.

**Granularidade**

`1 linha por item de pedido`, definida pela combinação:

- `order_id`
- `order_item_id`
- `product_id`
- `seller_id`

**Regras de negócio principais**

- `order_items` é a base factual principal
- `orders`, `customers`, `products`, `sellers` e `translation` entram por joins dimensionais
- `payments` e `reviews` são agregados no nível de `order_id` antes do join
- `total_item_value` = `price + freight_value`
- `delivery_time_days` mede o tempo entre compra e entrega
- `estimated_delay_days` mede a diferença entre entrega real e entrega estimada
- `is_delayed` indica entrega posterior à data estimada

## 3.1 Classificação de Sensibilidade

| Classe | Descrição | Exemplos no projeto |
| --- | --- | --- |
| `Analítico público` | Pode ser exposto em dashboard, markdown e prints sem granularidade sensível adicional. | métricas agregadas por categoria, tempo, UF, pagamento |
| `Analítico interno` | Necessário para engenharia, SQL e qualidade, mas não para exposição direta em app executivo. | `fact_orders_enriched` |
| `Quase-identificador` | Não identifica diretamente, mas pode aumentar risco por combinação. | `customer_city`, `seller_city`, `customer_zip_code_prefix`, `seller_zip_code_prefix`, timestamps detalhados |
| `Identificador pseudonimizado` | Chave mantida apenas para contagem, deduplicação e drill-down controlado. | `order_id` e `customer_unique_id` na camada publicada |

## 4. Dicionário de Colunas da `fact_orders_enriched`

| Coluna | Tipo de dado | Descrição | Regra de negócio | Observações de qualidade |
| --- | --- | --- | --- | --- |
| `order_id` | `string` | Identificador do pedido. | Chave de pedido oriunda de `orders`. | Sem nulos na base final. |
| `order_item_id` | `integer` | Sequencial do item dentro do pedido. | Diferencia itens em um mesmo pedido. | Parte da granularidade final. |
| `customer_id` | `string` | Identificador transacional do cliente. | Join com dimensão de clientes. | Sem nulos na base final. |
| `customer_unique_id` | `string` | Identificador único consolidado do cliente. | Permite análise de recorrência futura. | Pode repetir em vários `customer_id`. |
| `product_id` | `string` | Identificador do produto. | Join com dimensão de produtos. | Sem nulos na base final. |
| `seller_id` | `string` | Identificador do seller. | Join com dimensão de sellers. | Sem nulos na base final. |
| `order_status` | `string` | Status do pedido. | Oriundo da tabela `orders`. | Pode impactar leitura de entrega e review. |
| `order_purchase_timestamp` | `datetime` | Timestamp de compra do pedido. | Marco inicial do ciclo do pedido. | Sem nulos na base final. |
| `order_approved_at` | `datetime` | Timestamp de aprovação do pedido. | Referência para coerência temporal. | Pode ter ausências ou anomalias residuais da fonte. |
| `shipping_limit_date` | `datetime` | Data limite de envio do item. | Relacionada ao SLA operacional do seller. | Não necessariamente preenchida para todos os casos. |
| `order_delivered_carrier_date` | `datetime` | Data em que o pedido foi entregue ao transportador. | Marco intermediário do fluxo logístico. | Pode estar ausente em pedidos não entregues. |
| `order_delivered_customer_date` | `datetime` | Data de entrega ao cliente final. | Marco final da entrega. | Ausente em parte pequena da base; usado para derivações logísticas. |
| `order_estimated_delivery_date` | `datetime` | Data estimada de entrega. | Base para cálculo de atraso real. | Necessária para `is_delayed`. |
| `order_date` | `date` | Data-calendário da compra. | Derivada de `order_purchase_timestamp`. | Usada para agregações diárias. |
| `order_year` | `integer` | Ano da compra. | Derivado de `order_purchase_timestamp`. | Usado em análises temporais. |
| `order_month` | `integer` | Mês da compra. | Derivado de `order_purchase_timestamp`. | Usado em análises temporais. |
| `delivery_time_days` | `float` | Tempo entre compra e entrega, em dias. | `order_delivered_customer_date - order_purchase_timestamp`. | Nulo quando não há entrega registrada. |
| `estimated_delay_days` | `float` | Diferença entre entrega real e estimada, em dias. | `order_delivered_customer_date - order_estimated_delivery_date`. | Nulo quando não há entrega registrada. |
| `is_delayed` | `boolean` | Indicador de atraso na entrega. | `True` quando entrega real > entrega estimada. | Só é avaliado quando existe entrega registrada. |
| `price` | `float` | Valor do item. | Oriundo de `order_items`. | Valores negativos foram removidos no pipeline. |
| `freight_value` | `float` | Valor do frete do item. | Oriundo de `order_items`. | Valores negativos foram removidos no pipeline. |
| `total_item_value` | `float` | Valor total do item com frete. | `price + freight_value`. | Medida principal de receita por item. |
| `payment_count` | `integer` | Quantidade de eventos de pagamento do pedido. | Agregado por `order_id`. | Repetido para todos os itens do pedido. |
| `total_payment_value` | `float` | Soma do valor pago no pedido. | Agregado por `order_id`. | Pode diferir da soma de item + frete por regras transacionais da origem. |
| `max_payment_installments` | `integer` | Número máximo de parcelas usado no pedido. | Agregado por `order_id`. | Repetido para itens do mesmo pedido. |
| `payment_type_mode` | `string` | Meio de pagamento dominante do pedido. | Moda de `payment_type` por pedido. | Simplificação do comportamento real de pagamento. |
| `review_count` | `integer` | Quantidade de reviews associadas ao pedido. | Agregado por `order_id`. | Repetido para itens do mesmo pedido. |
| `review_score_mean` | `float` | Nota média de review do pedido. | Média de `review_score` por `order_id`. | Ausente quando não existe review. |
| `review_score_max` | `integer` | Maior nota de review do pedido. | Agregado por pedido. | Repetido por item. |
| `review_score_min` | `integer` | Menor nota de review do pedido. | Agregado por pedido. | Repetido por item. |
| `has_review_comment` | `integer` | Indicador de existência de comentário textual. | `1` se houver comentário não vazio em algum review do pedido. | Campo derivado agregando reviews. |
| `product_category_name` | `string` | Categoria do produto em português. | Oriunda da tabela de produtos. | Há pequena taxa de ausência. |
| `product_category_name_english` | `string` | Categoria do produto em inglês. | Enriquecida via tabela de tradução. | Pode estar ausente quando não há correspondência. |
| `product_name_lenght` | `float` | Comprimento do nome do produto. | Atributo cadastral do produto. | Nome original da fonte possui grafia `lenght`. |
| `product_description_lenght` | `float` | Comprimento da descrição do produto. | Atributo cadastral do produto. | Nome original da fonte possui grafia `lenght`. |
| `product_photos_qty` | `float` | Quantidade de fotos do produto. | Atributo cadastral do produto. | Pode conter ausências. |
| `product_weight_g` | `float` | Peso do produto em gramas. | Atributo físico do produto. | Pode conter ausências. |
| `product_length_cm` | `float` | Comprimento do produto em cm. | Atributo físico do produto. | Pode conter ausências. |
| `product_height_cm` | `float` | Altura do produto em cm. | Atributo físico do produto. | Pode conter ausências. |
| `product_width_cm` | `float` | Largura do produto em cm. | Atributo físico do produto. | Pode conter ausências. |
| `customer_zip_code_prefix` | `integer` | Prefixo do CEP do cliente. | Atributo de localidade do cliente. | Usado para segmentação geográfica. |
| `customer_city` | `string` | Cidade do cliente. | Atributo de localidade do cliente. | Não padronizado semanticamente no pipeline. |
| `customer_state` | `string` | UF do cliente. | Principal dimensão geográfica usada no projeto. | Usado em análises regionais e no mapa. |
| `seller_zip_code_prefix` | `integer` | Prefixo do CEP do seller. | Atributo de localidade do seller. | Suporta análises futuras de origem logística. |
| `seller_city` | `string` | Cidade do seller. | Atributo de localidade do seller. | Não utilizado diretamente nas análises principais. |
| `seller_state` | `string` | UF do seller. | Atributo de localidade do seller. | Pode ser explorado em análises futuras de supply. |
| `latest_review_creation_date` | `datetime` | Data mais recente de criação de review do pedido. | Agregado por `order_id`. | Nulo quando não há review. |
| `latest_review_answer_timestamp` | `datetime` | Data mais recente de resposta ao review. | Agregado por `order_id`. | Nulo quando não há review ou resposta. |

## 5. Camada Publicada para Dashboard

### `fact_orders_dashboard`

**Caminho**

- `data/published/dashboard/fact_orders_dashboard.parquet`

**Objetivo**

Camada publicada para o Streamlit, derivada de `fact_orders_enriched`, com minimização de dados e pseudonimização de chaves usadas apenas para contagem e drill-down controlado.

**Principais decisões**

- `order_id` e `customer_unique_id` permanecem apenas em formato pseudonimizado.
- `customer_id`, `product_id`, `seller_id`, cidade e prefixo de CEP não são publicados no dashboard.
- A camada mantém apenas colunas necessárias para responder às perguntas do case.

## 6. Observações Gerais de Qualidade

- A base final possui mais de `100.000` registros e atende ao volume mínimo esperado do case.
- A granularidade escolhida não apresentou duplicidade na validação de qualidade.
- `review_score_mean` e `product_category_name` apresentam baixa taxa de ausência.
- Existe uma pequena parcela de pedidos sem data final de entrega, o que gera nulos esperados em métricas logísticas derivadas.
- Existe uma anomalia residual da fonte em poucos registros nos quais a entrega aparece antes da aprovação; esse ponto foi mantido como alerta de qualidade, sem mascarar a informação original.

## 7. Uso Recomendado

Esta base é adequada para:

- análises de receita por categoria, estado e período
- análises de atraso e performance logística
- análises de experiência do cliente com base em reviews
- consumo em dashboard Streamlit
- consultas SQL em DuckDB

Para análises no nível de pedido, recomenda-se cuidado ao usar colunas agregadas por `order_id`, pois a base final preserva granularidade por item e replica alguns atributos de pedido em todas as linhas correspondentes.

Para consumo em dashboard e material executivo, recomenda-se usar preferencialmente `fact_orders_dashboard`, e não a camada interna `fact_orders_enriched`.


