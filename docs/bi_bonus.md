# Bônus de BI

## Objetivo

Este bônus foi preparado para ampliar a entrega do case com uma camada de consumo externa ao Streamlit, pronta para uso no Power BI.

A proposta é disponibilizar um modelo simples de fato e dimensões auxiliares, facilitando a montagem de um dashboard mais corporativo, com exploração ad hoc, relacionamento visual entre tabelas e distribuição futura em ambiente de BI.

Os exports foram mantidos analiticamente úteis, mas com pseudonimização das chaves e remoção de localização fina desnecessária, para refletir uma abordagem mais madura de privacidade por design.

## Arquivos Gerados

Os arquivos para Power BI ficam em:

- `data/processed/bi_exports/fact_sales_power_bi.csv`
- `data/processed/bi_exports/dim_date.csv`
- `data/processed/bi_exports/dim_product.csv`
- `data/processed/bi_exports/dim_payment.csv`
- `data/processed/bi_exports/dim_order_status.csv`
- `data/processed/bi_exports/dim_customer.csv`
- `data/processed/bi_exports/dim_seller.csv`

Todos os arquivos sao exportados com:

- delimitador explicito `;`
- encoding `utf-8-sig`
- `header=True`
- `index=False`

Esse padrao foi adotado para reduzir problemas de leitura em Power BI com configuracao regional em portugues do Brasil.

## Grain da Fato

A fato exportada em `fact_sales_power_bi.csv` possui:

- granularidade de `1 linha por item de pedido`
- chave primaria: `order_item_key`

## Chaves e Relacionamentos

### Dimensoes

- `dim_date[date_key]`
- `dim_product[product_key]`
- `dim_payment[payment_key]`
- `dim_order_status[order_status_key]`
- `dim_customer[customer_key]`
- `dim_seller[seller_key]`

### Foreign keys na fato

- `fact_sales_power_bi[date_key]`
- `fact_sales_power_bi[product_key]`
- `fact_sales_power_bi[payment_key]`
- `fact_sales_power_bi[order_status_key]`
- `fact_sales_power_bi[customer_key]`
- `fact_sales_power_bi[seller_key]`

### Observacao importante

As dimensoes `payment` e `order_status` passaram a usar chaves explicitas, evitando relacionamento por texto bruto e deixando o modelo estrela mais estavel para BI.

## Como Importar no Power BI

1. Abra o Power BI Desktop.
2. Selecione `Obter Dados` > `Texto/CSV`.
3. Importe todos os arquivos de `data/processed/bi_exports/`.
4. Se o Power BI ja tiver tabelas antigas importadas, remova as tabelas anteriores e reimporte os arquivos atualizados.
5. No modelo, configure os relacionamentos:
   - `fact_sales_power_bi[date_key]` -> `dim_date[date_key]`
   - `fact_sales_power_bi[product_key]` -> `dim_product[product_key]`
   - `fact_sales_power_bi[customer_key]` -> `dim_customer[customer_key]`
   - `fact_sales_power_bi[seller_key]` -> `dim_seller[seller_key]`
   - `fact_sales_power_bi[payment_key]` -> `dim_payment[payment_key]`
   - `fact_sales_power_bi[order_status_key]` -> `dim_order_status[order_status_key]`
6. Marque `dim_date` como tabela de datas, usando `order_date`.

## Observacao sobre `Column1`, `Column2`

Se alguma tabela aparecer com nomes genericos como `Column1`, `Column2` ou `Column3`, isso normalmente indica uma destas situacoes:

- importacao antiga mantida no modelo antes da regeneracao dos CSVs
- etapa de Power Query sem promocao correta do cabecalho
- leitura com configuracao de delimitador errada

Com os arquivos atuais, o comportamento esperado e:

- cabecalho real na primeira linha
- delimitador `;`
- colunas visiveis ja no preview do Power BI

## Estrutura das Tabelas

### `dim_date`

Colunas:

- `date_key`
- `order_date`
- `year`
- `quarter`
- `month`
- `month_name`
- `year_month`
- `week_of_year`
- `day`
- `weekday_name`

### `dim_product`

Colunas principais:

- `product_key`
- categoria em portugues
- categoria em ingles
- `category_label`
- atributos fisicos do produto

### `dim_payment`

Colunas principais:

- `payment_key`
- `payment_type`
- `payment_group`
- `payment_description`

### `dim_order_status`

Colunas principais:

- `order_status_key`
- `order_status`
- `status_group`
- `status_description`

### `dim_customer`

Colunas principais:

- `customer_key`
- `customer_master_key`
- `customer_state`

### `dim_seller`

Colunas principais:

- `seller_key`
- `seller_state`

## Quais Visuais Montar

Sugestão de visuais para uma página executiva:

- KPI cards:
  - receita total
  - total de pedidos
  - ticket médio
  - percentual de atraso
  - review médio

- Linha:
  - evolução mensal de receita

- Barra horizontal:
  - top categorias por receita

- Mapa preenchido ou bolhas:
  - receita por estado

- Colunas agrupadas:
  - receita por status do pedido

- Donut:
  - mix de receita por meio de pagamento

- Scatter:
  - categorias por atraso médio x receita

- Matriz:
  - estado x categoria com receita e atraso

## Análise Complementar Além do Streamlit

O Power BI permite aprofundar algumas leituras de forma complementar ao Streamlit:

- drill-down temporal por ano, trimestre, mês e dia
- navegação cruzada entre categoria, estado, seller e forma de pagamento
- matriz interativa para identificar combinações de maior receita e pior SLA
- comparação de performance entre grupos de status de pedido
- exploração mais livre por parte de recrutadores, gestores ou banca avaliadora

Enquanto o Streamlit entrega um storytelling mais guiado, o Power BI agrega exploração gerencial e experiência de BI mais tradicional.

## Como Este Bônus Aumenta o Valor da Entrega

Este bônus aumenta o valor do projeto por quatro motivos principais:

- mostra preocupação com interoperabilidade da camada analítica
- demonstra capacidade de estruturar dados para consumo em ferramenta de BI de mercado
- amplia a utilidade da entrega para público não técnico
- reforça a maturidade do projeto ao separar camada factual e dimensões auxiliares

Na prática, isso mostra que a solução não termina no código ou no dashboard customizado: ela também pode ser consumida em um fluxo analítico mais corporativo, com potencial de uso em ambiente executivo.
