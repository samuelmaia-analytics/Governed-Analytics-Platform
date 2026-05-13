-- Métricas operacionais por seller calculadas sobre a base de itens.
-- Encapsula a lógica de segmentação de volume_tier e SLA de entrega.
with items as (
    select * from {{ ref('stg_olist__order_items') }}
),

orders as (
    select * from {{ ref('stg_olist__orders') }}
),

base as (
    select
        i.seller_id,
        o.order_id,
        o.order_delivered_customer_date,
        o.order_purchase_timestamp,
        o.order_estimated_delivery_date,
        datediff('day', o.order_purchase_timestamp, o.order_delivered_customer_date)
            as delivery_time_days,
        case
            when o.order_delivered_customer_date is not null
             and o.order_estimated_delivery_date is not null
             and o.order_delivered_customer_date > o.order_estimated_delivery_date
            then 1 else 0
        end as is_delayed
    from items i
    left join orders o using (order_id)
),

seller_agg as (
    select
        seller_id,
        count(distinct order_id)    as seller_order_count,
        avg(delivery_time_days)     as seller_avg_delivery_days,
        avg(is_delayed)             as seller_delay_rate
    from base
    group by seller_id
)

select
    seller_id,
    seller_order_count,
    seller_avg_delivery_days,
    seller_delay_rate,
    case
        when seller_order_count <= 25  then 'long_tail'
        when seller_order_count <= 100 then 'scaled'
        when seller_order_count <= 500 then 'core'
        else 'strategic'
    end as seller_volume_tier
from seller_agg
