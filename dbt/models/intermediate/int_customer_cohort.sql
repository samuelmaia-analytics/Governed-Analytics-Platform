-- Atributos de cohort e recorrência calculados por customer_unique_id.
-- A lógica de cohort_order_month_number permite análises de retenção.
with orders as (
    select * from {{ ref('stg_olist__orders') }}
),

customers as (
    select * from {{ ref('stg_olist__customers') }}
),

order_customer as (
    select
        o.order_id,
        o.order_purchase_timestamp,
        c.customer_unique_id
    from orders o
    left join customers c using (customer_id)
    where c.customer_unique_id is not null
),

with_cohort as (
    select
        *,
        min(order_purchase_timestamp) over (
            partition by customer_unique_id
        ) as customer_first_purchase_timestamp
    from order_customer
),

with_sequence as (
    select
        order_id,
        customer_unique_id,
        order_purchase_timestamp,
        customer_first_purchase_timestamp,
        -- Número de meses desde a primeira compra
        (year(order_purchase_timestamp)  - year(customer_first_purchase_timestamp))  * 12
        + (month(order_purchase_timestamp) - month(customer_first_purchase_timestamp))
            as cohort_order_month_number,
        -- Sequência de pedidos do cliente (1 = primeiro pedido)
        dense_rank() over (
            partition by customer_unique_id
            order by min(order_purchase_timestamp) over (
                partition by customer_unique_id, order_id
            )
        ) as customer_order_sequence
    from with_cohort
)

select
    order_id,
    customer_unique_id,
    customer_first_purchase_timestamp,
    cohort_order_month_number,
    customer_order_sequence,
    customer_order_sequence = 1 as is_first_order,
    strftime(customer_first_purchase_timestamp, '%Y-%m') as purchase_cohort_month
from with_sequence
